#
# Copyright (c) 2011, 2013 Adam Tauno Williams <awilliam@whitemice.org>
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

class RowField(object):
    pass

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
            return 'Expected {0} value but got "{1}" {2} in column "{3}".'.format( expected, got, type( got ), name )

        #TODO: Handle cell type "xlrd.XL_CELL_ERROR".
        #TODO: Read cell formatting info?
        row = []

        for field in self._definition.get( 'columns' ):
            isNull = False

            tmp = RowField( )
            #Check if field names in description match field names in XLS doc.
            tmp.field_value    = field.get( 'static', None ) # The field has a static value!
            tmp.field_default  = field.get( 'default', None )
            tmp.field_kind     = field.get( 'kind', 'string' )
            tmp.field_name     = field.get( 'name', None )
            tmp.field_iskey    = unicode( field.get( 'key', 'false' ) ).lower()
            tmp.field_null     = False
            tmp.field_case     = field.get( 'coerceVia', None )
            tmp.field_lower    = field.get( 'lower', False )
            tmp.field_upper    = field.get( 'upper', False )
            tmp.field_divisor  = field.get( 'divisor', 1 )
            tmp.field_floor    = field.get( 'floor', None )
            tmp.field_ceiling  = field.get( 'ceiling', None )
            tmp.field_required = field.get( 'required', False )
            tmp.field_target   = field.get( 'rename', tmp.field_name ).replace( ' ', '-' )
            tmp.field_cast     = field.get( 'coerceVia', None )

            if tmp.field_value:
                # This is a static value, we don't care what is in the file
                pass

            elif tmp.field_name in self._column_names:
                # Process a column that IS FOUND IN THE SHEET
                try:
                    if tmp.field_value is None:

                        # This columen will be processed from the sheet as the value is not static!
                        self._colNum = self._column_names.index( tmp.field_name )
                        tmp.field_value = self._sheet.cell( self._rowNum, self._colNum ).value

                        # Empty
                        if tmp.field_value in [ empty_cell.value, None ]:
                            tmp.field_null = True

                        # booleanString, booleanInteger
                        elif tmp.field_kind in ( 'booleanString', 'booleanInteger' ) :
                            if value in [ 0, 1 ]:
                                if tmp.field_kind in ( 'booleanString' ):  tmp.field_value = unicode( bool( tmp.field_value ) )
                                if tmp.field_kind in ( 'booleanInteger' ): tmp.field_value = int( tmp.field_value )
                            else:
                                raise TypeError( get_type_error_message( 'boolean', tmp.field_value, tmp.field_name ) )

                        # String
                        elif tmp.field_kind in ( 'string' ):
                            if not isinstance( tmp.field_value, basestring ):
                                # coerceVia allows a non-string value to be read in as a string
                                if tmp.field_cast:
                                    for cast in tmp.field_cast:
                                        try:
                                            if cast == 'integer':  tmp.field_value = int( tmp.field_value )
                                            elif cast == 'float':  tmp.field_value = float( tmp.field_value )
                                            elif cast == 'string': tmp.field_value = unicode( tmp.field_value )
                                        except Exception, e:
                                            raise TypeError( 'Unable to coerce value "{0}" to type "{1}"'.format( value, cast ) )
                                    tmp.field_value = unicode( tmp.field_value )
                            if isinstance( tmp.field_value, basestring ):
                                if tmp.field_lower: value = value.lower( )
                                if tmp.field_upper: value = value.upper( )
                            else:
                                raise TypeError( get_type_error_message( 'string', tmp.field_value, tmp.field_name ) )

                        # Date
                        elif tmp.field_kind in ( 'date' ):
                            # TODO: shouldn't we pass the books datemode?
                            date_value = str( xldate_as_tuple( tmp.field_value, self._datetype )[ 0:3 ] )
                            tmp.field_value = SimpleXLSFormat.Reformat_Date_String\
                                                ( date_value, '(%Y, %m, %d)', '%Y-%m-%d')
                        # Time
                        elif tmp.field_kind in ( 'time' ):
                            time_value = xldate_as_tuple( field_value, self._datetype )[ 3: ]
                            field_value = '{0:02d}:{1:02d}:{2:02d}'.format( *time_value )

                        # DateTime
                        elif tmp.field_kind in ( 'datetime' ):
                            date_value = unicode( xldate_as_tuple( tmp.field_value, self._datetype ) )
                            tmp.field_value = SimpleXLSFormat.Reformat_Date_String\
                                        ( date_value, '(%Y, %m, %d, %H, %M, %S)', '%Y-%m-%d %H:%M:%S' )

                        # Integer, float, ifloat
                        elif tmp.field_kind in ( 'integer', 'float', 'ifloat' ):

                            if tmp.field_kind == 'integer':
                                # Integer
                                tmp.field_value = int( tmp.field_value )
                                if tmp.field_floor is not None:   floor = int( tmp.field_floor )
                                if tmp.field_ceiling is not None: ceiling = int( tmp.field_ceiling )
                                if tmp.field_divisor != 1:
                                    tmp.field_value = tmp.field_value / int( tmp.field_divisor )
                            else:
                                # Float
                                tmp.field_value = float( tmp.field_value )
                                if tmp.field_floor is not None:   tmp.field_floor = float( tmp.field_floor )
                                if tmp.field_ceiling is not None: tmp.field_ceiling = float( tmp.field_ceiling )
                                if tmp.field_divisor != 1:
                                    tmp.field_value = tmp.field_value / float( tmp.field_divisor )

                            # Floor test
                            if (tmp.field_floor is not None) and ( tmp.field_value < tmp.field_floor ):
                                message = 'Value {0} below floor {1}'.format( tmp.field_value, tmp.field_floor )
                                raise ValueError(message)

                            # Cieling Test
                            if (tmp.field_ceiling is not None) and (tmp.field_value > tmp.field_ceiling):
                                message = 'Value {0} above ceiling {1}'.format( tmp.field_value, tmp.field_ceiling )
                                raise ValueError(message)


                except (ValueError, TypeError), e:
                    raise RecordFormatException(str(e))

            else:

                # Process a column that NOT FOUND IN THE SHEET

                if not tmp.field_required:
                    # Field is NOT required, we use the specified default value
                    tmp.field_value = tmp.field_default
                    if tmp.field_value is None:
                        tmp.field_null = True
                else:
                    message = (' \n  Field name \"{0}\" given in description, but not found'
                            ' in XLS input document.').format( tmp.field_name )
                    raise RecordFormatException(message)

            row.append( tmp )

        # RENDER ROW
        with self.xml.container( 'row', attrs={ 'id': unicode( self._rowNum ) } ) as xml:
            for tmp in row:
                if tmp.field_null:
                    xml.element( tmp.field_target, attrs={ 'dataType': tmp.field_kind,
                                                           'isNull':   'true',
                                                           'isPrimaryKey': tmp.field_iskey } )
                else:
                    xml.element( tmp.field_target, text = unicode( tmp.field_value),
                                                   attrs = { 'dataType': tmp.field_kind,
                                                             'isNull':   'false',
                                                             'isPrimaryKey': tmp.field_iskey } )
        return True

    def process_record_out(self, record):
        raise NotImplementedException('Cannot write XLS documents.')

