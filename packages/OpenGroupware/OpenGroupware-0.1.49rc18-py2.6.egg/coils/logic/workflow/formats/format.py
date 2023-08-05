#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import logging, inspect, pickle, yaml
from datetime         import datetime
from time             import sleep
from lxml             import etree
from xml.sax.saxutils import escape, unescape
from coils.foundation import *
from coils.core       import *
from exception        import RecordFormatException

#
# Error message 0 is OK, Error codes -1 ... -99 reserved for base class
#
COILS_FORMAT_DESCRIPTION_OK         = 0
COILS_FORMAT_DESCRIPTION_INCOMPLETE = -1

class Format(object):
    FORMATTERS = None

    def __init__(self):
        self.log = logging.getLogger('workflow')

    def set_description(self, fd):
        self._reject_file = None
        self._discard_on_error = False
        if (('name' in fd) and
            ('class' in fd) and
            ('data' in fd)):
            self._chunk_size = int(fd.get('chunkSize', 1000))
            self._chunk_delay = float(fd.get('chunkDelay', 0.5))
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')
        else:
            return (COILS_FORMAT_DESCRIPTION_INCOMPLETE, 'Incomplete Description')

    def pause(self, counter):
        if (self._chunk_size == 0):
            return
        elif ((counter % self._chunk_size) == 0):
            sleep(self._chunk_delay)

    def load_description(self, name):
        filename = 'wf/f/{0}.pf'.format(name)
        handle = BLOBManager.Open(filename, 'rb', encoding='binary')
        data = pickle.load(handle)
        BLOBManager.Close(handle)
        return self.set_description(data)

    def save(self):
        filename = 'wf/f/{0}.pf'.format(self.description.get('name'))
        handle = BLOBManager.Create(filename, encoding='binary')
        pickle.dump(self.description, handle)
        BLOBManager.Close(handle)
        return True

    @property
    def mimetype(self):
        return 'application/xml'

    def get_name(self):
        return self.description.get('name')

    def encode_text(self, text):
        return escape(text)

    def decode_text(self, text):
        return unescape(text)

    def next_record(self):
        raise NotImplementedException()

    def process_record(self, record):
        raise NotImplementedException()

    @property
    def reject_buffer(self):
        if (self._reject_file is None):
            self._reject_file = BLOBManager.ScratchFile()
        return self._reject_file

    def reject(self, data, message=None):
        #self.reject_buffer.write(message)
        self.reject_buffer.write(data)

    def process_in(self, rfile, wfile):
        self._input = rfile
        self._result = []
        wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        wfile.write(u'<ResultSet formatName=\"{0}\" className=\"{1}\" tableName="{2}">'.\
            format(self.description.get('name'),
                   self.__class__.__name__,
                   self.description.get('tableName', '_undefined_')))
        counter = 0
        while (True):
            # TODO: Support discardMalformedRecords parameter [self._discard_on_error]?
            record = self.next_record_in()
            counter += 1
            self.pause(counter)
            if (record is None):
                break
            try:
                data = self.process_record_in(record)
            except RecordFormatException, e:
                self.reject(record)
                self.log.warn('Record format exception on record {0}: {1}'.format(self.in_counter, record))
                if (self._discard_on_error):
                    self.log.info('Record {0} of input message dropped due to format error'.format(self.in_counter))
                else:
                    raise e
            else:
                if (data is not None):
                    wfile.write(data)
        wfile.write(u'</ResultSet>')
        return

    def begin_output(self):
        pass

    def end_output(self):
        pass

    def as_yaml(self):
        return yaml.dump(self.description)

    def process_out(self, rfile, wfile):
        doc = etree.parse(rfile)
        self.begin_output()
        for record in doc.xpath(u'/ResultSet/row'):
            data = self.process_record_out(record)
            if (data is not None):
                wfile.write(data)
        self.end_output()
        return

    @staticmethod
    def Create_Date_Value(date_string, in_format):
        return StandardXML.Create_Date_Value(date_string, in_format)

    @staticmethod
    def Reformat_Date_String(date_string, in_format, out_format):
        return StandardXML.Reformat_Date_String(date_string, in_format, out_format)

    @staticmethod
    def Load_Formatters():
        Format.FORMATTERS = { }
        bundle =  __import__('coils.logic.workflow.formats', fromlist=['*'])
        for name, data in inspect.getmembers(bundle, inspect.isclass):
            # Only load classes specifically from this bundle
            if (data.__module__[:len(bundle.__name__)] == bundle.__name__):
                if(issubclass(data, Format)):
                    logging.getLogger('workflow').info('Format class {0} loaded'.format(name))
                    Format.FORMATTERS[name] =  data

    @staticmethod
    def Marshall(name):
        if (Format.FORMATTERS is None):
            Format.Load_Formatters()
        if (name in Format.FORMATTERS):
            return Format.FORMATTERS.get(name)()
        return None

    @staticmethod
    def Load(name):
        filename = u'wf/f/{0}.pf'.format(name)
        handle = BLOBManager.Open(filename, 'rb', encoding='binary')
        description = pickle.load(handle)
        BLOBManager.Close(handle)
        format = Format.Marshall(description.get('class'))
        code = format.set_description(description)
        if (code[0] == COILS_FORMAT_DESCRIPTION_OK):
            return format
        raise CoilsException(code[1])

    @staticmethod
    def LoadYAML(name):
        format = Format.Load(name)
        return format.as_yaml()

    @staticmethod
    def Delete(name):
        return BLOBManager.Delete('wf/f/{0}.pf'.format(name))

    @staticmethod
    def ListFormats():
        result = [ ]
        for name in BLOBManager.List('wf/f/'):
            result.append(name[:-3])
        return result
