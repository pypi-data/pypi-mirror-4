#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from xlrd          import xldate_as_tuple, empty_cell
from format        import COILS_FORMAT_DESCRIPTION_OK
from format        import COILS_FORMAT_DESCRIPTION_INCOMPLETE
from xls_format import SimpleXLSFormat
from exception   import RecordFormatException

class ColumnarXLSReaderFormat(SimpleXLSFormat):

    def __init__(self):
        SimpleXLSFormat.__init__(self)

    def set_description(self, fd):
        code = SimpleXLSFormat.set_description(self, fd)
        error = [COILS_FORMAT_DESCRIPTION_INCOMPLETE]
        if (code[0] == 0):
            # TODO: Verify XLS format parameters
            self.description = fd
            self._definition = self.description.get('data')
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')
        else:
            return code

    @property
    def mimetype(self):
        return 'application/vnd.ms-excel'

    def process_record_in(self):
        
        def get_type_error_message(expected, got, name):
            return 'Expected {0} value but got "{1}" {2} in column "{3}".'.format(expected, value, type(value), field['name'])
            
        #TODO: Handle cell type "xlrd.XL_CELL_ERROR".
        #TODO: Read cell formatting info?
        row = []
        isKey = False
        for field in self._definition.get('columns'):
            isNull = False
            #Check if field names in description match field names in XLS doc.
            value = field.get('static', None)
            if value:
                # This is a static value, we don't care what is in the file
                pass
            elif field['name'] in self._column_names:
                try:
                    isKey = str(field.get('key', 'false')).lower()
                    if (value is None):
                        self._colNum = self._column_names.index(field['name'])
                        value = self._sheet.cell(self._rowNum, self._colNum).value

                        # Empty
                        if value in [empty_cell.value, None]:
                            isNull = True
                            
                        # booleanString, booleanInteger
                        elif (field['kind'] in ['booleanString', 'booleanInteger']):
                            if value in [0, 1]:
                                if field['kind'] in ['booleanString']: value = str(bool(value))
                                if field['kind'] in ['booleanInteger']: value = int(value)
                            else:
                                raise TypeError(get_type_error_message( 'boolean', value, field['name'] ) )
                                
                        # String
                        elif (field['kind'] in ['string']):
                            if not isinstance(value, basestring):
                                cast_as = field.get('coerceVia', None)
                                if cast_as:
                                    for cast in cast_as:
                                        try:
                                            if cast == 'integer': value = int(value)
                                            elif cast == 'float': value = float(value)
                                            elif cast == 'string': value = unicode(value)
                                        except Exception, e:
                                            raise TypeError('Unable to coerce value "{0}" to type "{1}"'.format(value, cast))
                                    value = unicode(value)
                            if isinstance(value, basestring):
                                if (field.get('lower', False)): value = value.lower()
                                elif (field.get('upper', True)): value = value.upper()                            
                            elif not isinstance(value, basestring):
                                raise TypeError(get_type_error_message( 'string', value, field['name'] ) )
                        elif (field['kind'] in ['date']):
                            # TODO: shouldn't we pass the books datemode?
                            date_value = str(xldate_as_tuple(value, self._datetype)[0:3])
                            value = SimpleXLSFormat.Reformat_Date_String\
                                                (date_value, '(%Y, %m, %d)', '%Y-%m-%d')
                        # Time
                        elif (field['kind'] in ['time']):
                            time_value = xldate_as_tuple(value, self._datetype)[3:]
                            value = '{0:02d}:{1:02d}:{2:02d}'.format( *time_value )
                            
                        # DateTime
                        elif (field['kind'] in ['datetime']):
                            date_value = str(xldate_as_tuple(value, self._datetype))
                            value = SimpleXLSFormat.Reformat_Date_String\
                                        (date_value, '(%Y, %m, %d, %H, %M, %S)', '%Y-%m-%d %H:%M:%S')
                                        
                        # Integer, float, ifloat
                        elif (field['kind'] in ['integer', 'float', 'ifloat']):
                            divisor = field.get('divisor', 1)
                            floor = field.get('floor', None)
                            ceiling = field.get('ceiling', None)
                            if (field['kind'] == 'integer'):
                                value = int(value)
                                if (floor is not None): floor = int(floor)
                                if (ceiling is not None): ceiling = int(ceiling)
                                if (divisor != 1):
                                    value = value / int(divisor)
                            else:
                                # Float
                                value = float(value)
                                if (floor is not None): floor = float(floor)
                                if (ceiling is not None): ceiling = float(ceiling)
                                if (divisor != 1):
                                    value = value / float(divisor)
                            if (floor is not None) and (value < floor):
                                message = 'Value {0} below floor {1}'.format(value, floor)
                                raise ValueError(message)
                            if (ceiling is not None) and (value > ceiling):
                                message = 'Value {0} above ceiling {1}'.format(value, ceiling)
                                raise ValueError(message)
                                
                except (ValueError, TypeError), e:
                    raise RecordFormatException(str(e))
                    
            else:
                
                # The field in description does not exist in the sheet
                if field.get('required', False):
                    # Field is not required, we use the specified default value
                    value = field.get('default', None)
                    if (value is None):
                        isNull = True
                        message = ('Field \"{0}\" marked \"required\", not found in XLS input \n'
                               ' document and no default value given: row {1} column {2}.')\
                               .format(field['name'], self._rowNum, self._colNum+1)
                        self.log.info(message)
                else:
                    message = (' \n  Field name \"{0}\" given in description, but not found'
                            ' in XLS input document.').format(field['name'])
                    raise RecordFormatException(message)
                    
            name = field.get('rename', field['name'])
            name = name.replace(' ', '-')
            
            if (isNull):
                row.append(u'<{0} dataType=\"{1}\" isNull=\"true\" isPrimaryKey=\"{2}\"/>'.\
                    format(name, field['kind'], isKey))
            else:
                if isinstance(value, basestring):
                    value = self.encode_text(value)
                row.append(u'<{0} dataType=\"{1}\" isNull=\"false\" isPrimaryKey=\"{2}\">{3}</{4}>'.\
                    format(name, field['kind'], field.get('key', 'false'), value, name))
        return u'<row>{0}</row>'.format(u''.join(row))


    def process_record_out(self, record):
        raise NotImplementedException('Cannot write XLS documents.')
