#
# Copyright (c) 2009, 2011 Adam Tauno Williams <awilliam@whitemice.org>
# Contributions by Adam Seskunas
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
import StringIO
from format               import COILS_FORMAT_DESCRIPTION_OK, Format
from format               import COILS_FORMAT_DESCRIPTION_INCOMPLETE
from line_oriented_format import LineOrientedFormat
from exception            import RecordFormatException

class SimpleFixedFieldFormat(LineOrientedFormat):
    #TODO: Issue#96, SimpleDelimitedFieldFormat should support static values - COMPLETE
    #TODO: Issue#148, SimpleDelimitedFieldFormat should output static values if the static
    #                 field contains a start & end attribtues.

    def __init__(self):
        LineOrientedFormat.__init__(self)

    def set_description(self, fd):
        code = LineOrientedFormat.set_description(self, fd)
        error = [COILS_FORMAT_DESCRIPTION_INCOMPLETE]
        field_check = False
        field_name = None
        for field in fd['data']['fields']:
            if ('static' not in field):
                # Non-static-value fields must have a "start" and "end" attribute.
                if (('start' not in field) or ('end' not in field)):
                    field_check = True
                    field_name = field['name']
                    break
        if (code[0] != 0):
            return code
        elif ('recordLength' not in fd['data']):
            error.append('RecordLength missing from description')
            return error
        elif (fd['data']['recordLength'] is None):
            error.append('RecordLength is not defined')
            return error
        elif (field_check):
            error.append('Field: <{0}> is missing start or end positition'.format(field_name))
            return error
        else:
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')

    @property
    def mimetype(self):
        return 'text/plain'

    def process_record_in(self, record):
        row = []
        self.in_counter = self.in_counter + 1
        if (self.in_counter <= self._skip_lines):
            self.log.debug('skipped initial line {0}'.format(self.in_counter))
            return None
        if ((record[0:1] == '#') and (self._skip_comment)):
            self.log.debug('skipped commented line{0}'.format(self.in_counter))
            return None
        record  = ''.join([c for c in record if ((127 > ord(c) > 31) or ord(c) in self._allowed_ords)])
        if ((len(record) == 0) and (self._skip_blanks)):
            self.log.debug('skipped blank line {0}'.format(self.in_counter))
            return None
        for field in self._definition.get('fields'):
            isKey = str(field.get('key', 'false')).lower()
            try:
                isNull = False
                value = field.get('static', None)
                if (value is None):
                    value = record[(field['start'] - 1):(field['end'])]
                    if (field['kind'] in ['integer', 'float', 'ifloat']):
                        divisor = field.get('divisor', 1)
                        floor = field.get('floor', None)
                        cieling = field.get('cieling', None)
                        if (field.get('sign', 'u') == 'a'):
                            sign  = value[-1:] # Take last character as sign
                            value = value[:-1] # Drop last character
                        elif (field.get('sign', 'u') == 'b'):
                            sign = value[0:1] # Take first character as sign
                            value = value[1:] # Drop first character
                        elif (field.get('sign', 'u') == 'u'):
                            sign = value[0:1]
                            if (sign == '-'):
                                value = value[1:]
                            else:
                                sign = '+'
                        else:
                            sign = '+'
                        #self.log.debug('sign character for field {0} is {1}'.format(field['name'], sign))
                        if (sign == '-'):
                            sign = -1
                        else:
                            sign = 1
                        value = value.strip()
                        if (len(value) == 0):
                            isNull = True
                        elif (field['kind'] == 'integer'):
                            value = (int(float(value)) * int(sign))
                            if (floor is not None): floor = int(floor)
                            if (cieling is not None): cieling = int(cieling)
                            if (divisor != 1):
                                value = value / int(divisor)
                        else:
                            value = (float(value) * float(sign))
                            if (floor is not None): floor = float(floor)
                            if (cieling is not None): cieling = float(cieling)
                            if (divisor != 1):
                                value = value / float(field['divisor'])
                        if (isNull is False):
                            if (floor is not None) and (value < floor):
                                message = 'Value {0} below floor {1}'.format(value, floor)
                                self.log.warn(message)
                                raise ValueError(message)
                            if (cieling is not None) and (value > cieling):
                                message = 'Value {0} above cieling {1}'.format(value, cieling)
                                self.log.warn(message)
                                raise ValueError(message)
                    elif field['kind'] in ('date'):
                        if value:
                            value = Format.Reformat_Date_String(value, field['format'], '%Y-%m-%d')
                        else:
                            isNull = True
                    elif field['kind'] in ('datetime'):
                        if value:
                            value = Format.Reformat_Date_String(value, field['format'], '%Y-%m-%d %H:%M:%S')
                        else:
                            isNull = True
                    else:
                        if (field.get('strip', False)):
                            value = value.strip()
                        value = self.encode_text(value)
            except ValueError, e:
                message = 'Value error converting value \"{0}\" to type \"{1}\" for attribute \"{2}\".'.\
                    format(value, field['kind'], field['name'])
                self.log.warn(message)
                raise RecordFormatException(message, e)
            if (isNull):
                row.append(u'<{0} dataType=\"{1}\" isNull=\"true\" isPrimaryKey=\"{2}\"/>'.\
                    format(field['name'], field['kind'], isKey))
            else:
                row.append(u'<{0} dataType=\"{1}\" isNull=\"false\" isPrimaryKey=\"{2}\">{3}</{4}>'.\
                    format(field['name'], field['kind'], isKey,  value, field['name']))
        return u'<row>{0}</row>'.format(u''.join(row))

    def process_record_out(self, record):
        record_length = int(self.description['data']['recordLength'])
        stream = StringIO.StringIO(''.rjust(record_length, ' '))
        for field in self._definition.get('fields'):
            self.out_counter = self.out_counter + 1
            if 'static' in field:
                if 'start' in field:
                    start = int(field.get('start'))
                    value = unicode(field.get('static'))
                    length = len(value)
                    pad = field.get('pad', ' ')
                    stream.seek((start - 1), 0)
                    stream.write(value.ljust(length, pad))
            else:
                start = int(field.get('start'))
                self.log.debug('Record#{0}: seeking field start position {1}.'.format(self.out_counter, start))
                stream.seek((start - 1), 0)
                pad = field.get('pad', ' ')
                length = ((field['end'] - field['start']) + 1)
                value = record.xpath('./{0}/text()'.format(field['name']))
                if (len(value) == 1):
                    value = unicode((self.decode_text(value[0])))
                else:
                    value = field.get('default', u'')
                if field['kind'] in ('integer', 'float', 'ifloat'):
                    #print '{0}: kind={1} divisor={2} input={3}'.format(field['name'], field['kind'], field['divisor'], value)
                    if (len(value) == 0):
                        value = u'0'
                    divisor = field.get('divisor', '1')
                    if (field['kind'] == 'integer'):
                        value = int(float(value)) * int(divisor)
                    elif (field['kind'] in ['float', 'ifloat']):
                        value = float(value) * float(divisor)
                        if (field['kind'] == 'ifloat'):
                            value = int(value)
                    if (value < 0):
                        sign = u'-'
                    else:
                        sign = u'+'
                    if ((field['sign'] == 'b') or (field['sign'] == 'a')):
                        length = length - 1
                        value = unicode(str(abs(value)))
                        if (field['sign'] == 'b'):
                            stream.write(sign)
                    elif field.get('sign', 'u') == 'u':
                        if value < 0:
                            value = '-{0}'.format(unicode(str(abs(value))))
                        else:
                            value = unicode(str(abs(value)))
                    stream.write(value.rjust(length, pad))
                    if (field['sign'] == 'a'):
                        stream.write(sign)
                    #print '  Value={0}'.format(value)
                elif field['kind'] in ('datetime', 'date'):
                    if field['kind'] == 'date':
                        in_format = '%Y-%m-%d'
                    else:
                        in_format = '%Y-%m-%d %H:%M:%S'
                    out_format = field.get('format', in_format)
                    if value:
                        value = Format.Reformat_Date_String(value, in_format, out_format)
                    else:
                        value = ''
                    stream.write(value.ljust(length, pad))
                else:
                    #pad = field.get('pad', u' ')
                    stream.write(value.rjust(length, pad))
        # append line break character(s) to end-of-record
        stream.seek(record_length, 0)
        for ordinal in self._line_delimiter:
            stream.write(chr(ordinal))
        row = stream.getvalue()
        stream.close()
        return row

