# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import api_dif as dif
from lxml             import etree
from xml.sax.saxutils import escape, unescape
from format           import COILS_FORMAT_DESCRIPTION_OK, Format

# WARN: Current import only

class DIFField(object):
    # TODO: Implement "divisor" directive
    # TODO: Implement "sign" directive [values: a/b for after/before]
    # TODO: Implement "string"
    # TODO: Implement "nullValue"
    # TODO: Implement "upper"
    
    def __init__(self, description):
        self.c = description
    
    @property
    def kind(self):
        return self.c['kind']
        
    @property
    def name(self):
        return self.c['name']
        
    @property
    def is_key(self):
        if self.c.get('key', False):
            return 'true'
        return 'false'
        
    def preprocess_string(self, value):
        if not isinstance(value, unicode):
            value = unicode(value)
        if value:
            if self.c.get('upper', False):
                value = value.uppwer()
            if self.c.get('lower', False):
                value = value.uppwer()
        if value == self.c.get('nullValue', None):
            return None
        return value

    def preprocess_integer(self, value):
        # TODO: Implement floor
        # TODO: Implement divisor
        # TODO: Implement cieling
        if not isinstance(value, int):
            value = int(value)
        if value == self.c.get('nullValue', None):
            return None
        return value
        
    def preprocess_float(self, value):
        # TODO: Implement floor
        # TODO: Implement divisor
        # TODO: Implement cieling
        if not isinstance(value, float):
            value = float(value)
        if value == self.c.get('nullValue', None):
            return None
        return value        
        
    def preprocess(self, value):
        if isinstance(value, basestring):
            if self.c.get('strip', False):
                value = value.strip()
        if self.kind == 'string':
            value = self.preprocess_string(value)
        elif self.kind == 'integer':
            value = self.preprocess_integer(value)
        elif self.kind == 'float':
            value = self.preprocess_float(value)
        else:
            raise CoilsException('Unsupported data type for format class SimpleDIFFormat')
        return value

    def encode(self, value):
        value = self.preprocess(value)
        if value is None:
            return u'<{0} dataType=\"{1}\" isNull=\"true\" isPrimaryKey=\"{2}\"/>'.\
                format(self.name, self.kind, self.is_key)
        else:
            return u'<{0} dataType=\"{1}\" isNull=\"false\" isPrimaryKey=\"{2}\">{3}</{0}>'.\
                format(self.name, self.kind, self.is_key,  escape(unicode(value)))


class SimpleDIFFormat(Format):
    #TODO: Import export support (low-priority)

    def __init__(self):
        Format.__init__(self)
        self._styles = None
        self._fields = [ ]

    def set_description(self, fd):
        code = Format.set_description(self, fd)
        if (code[0] == 0):
            self.description = fd
            self._definition = self.description.get('data')
            # TODO: Check that every field has at least: kind
            self._skip_lines     = int(self._definition.get('skipLeadingLines', 0))            
            for column in self._definition.get('columns'):
                self._fields.append(DIFField(column))
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')
        else:
            return code

    @property
    def mimetype(self):
        # TODO: correct?
        return 'application/dif'

    def process_in(self, rfile, wfile):
        dir(dif)
        self.in_counter = 0
        sheet = dif.DIF(rfile)
        self._input = rfile
        self._result = []
        wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        wfile.write(u'<ResultSet formatName=\"{0}\" className=\"{1}\">'.format(self.description.get('name'),
                                                                              self.__class__.__name__))
        for record in sheet.data:
            data = self.process_record_in(record)
            if (data is not None):
                wfile.write(data)
        wfile.write(u'</ResultSet>')
        return

    def process_record_in(self, record):
        row = []
        self.in_counter = self.in_counter + 1
        if (self.in_counter <= self._skip_lines):
            self.log.debug('skipped initial line {0}'.format(self.in_counter))
            return None
        for counter in range(0,len(self._fields)):
            row.append(self._fields[counter].encode(record[counter]))
        return u'<row>{0}</row>'.format(u''.join(row))

    def process_out(self, rfile, wfile):
        raise NotImplementedException()

    def process_record_out(self, record):
        raise NotImplementedException()
