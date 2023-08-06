#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime            import datetime
from xml.sax.saxutils    import escape, unescape
from lxml                import etree

class StandardXML(object):

    @staticmethod
    def Create_Date_Value(date_string, in_format):
        return datetime.strptime(date_string.strip(), in_format)

    @staticmethod
    def Reformat_Date_String(date_string, in_format, out_format):
        return StandardXML.Create_Date_Value(date_string, in_format).strftime(out_format)

    @staticmethod
    def Convert_Field_To_Value(field):
        is_null   = field.attrib.get( 'isNull', 'false' ).lower( )
        if is_null == 'true':
            return None
        else:
            value = field.text
            data_type = field.attrib.get( 'dataType', 'string' ).lower()
            if data_type in ( 'string', 'char', 'varchar' ):
                if value is not None:
                    value = unescape( value )
            elif data_type in ( 'float', 'decimal' ):
                value = float( value )
            elif data_type in ( 'integer', 'serial', 'smallint' ):
                value = int( value )
            elif data_type in ( 'date' ):
                value = datetime.strptime( value, '%Y-%m-%d' )
            elif data_type in [ 'datetime', ]:
                value = datetime.strptime( value, '%Y-%m-%d %H:%M:%S' )
            elif data_type in [ 'time', ]:
                if len( value ) > 4:
                    value = datetime.strptime( value, '%H:%M:%S' )
                else:
                    value = datetime.strptime( value, '%H:%M' )
            else:
                raise Exception( 'Unexpected dataType "{0}" encountered.'.format( data_type ) )
            return value

    @staticmethod
    def Parse_Row(row, keys=[]):
        fields = {}
        keys   = {}
        for field in row.iterchildren():
            name  = field.tag.lower()
            # Determine if value is primary key
            is_key = field.attrib.get('isPrimaryKey', 'false').lower()
            if (name in keys) or (is_key == 'true'):
                is_key = 'true'
            # Process field value
            value = StandardXML.Convert_Field_To_Value(field)
            # Set as key or value
            if (is_key == 'true'):
                keys[name] = value
            else:
                fields[name] = value
        return keys, fields

    @staticmethod
    def Read_ResultSet_Metadata(handle):
        handle.seek(0)
        table_name = None
        format_name = None
        format_class = None
        for event, element in etree.iterparse(handle, events=("start", "end")):
          if (event == 'start' and element.tag == 'ResultSet'):
            table_name = element.attrib.get('tableName')
            format_name = element.attrib.get('formatName')
            format_class = element.attrib.get('className')
            break
        return table_name, format_name, format_class

    @staticmethod
    def Read_Rows(handle, pkeys=[], for_operation = None):
        # TODO: Only process rows between Result tags?
        handle.seek(0)
        if not for_operation: for_operation = 'any'
        for event, element in etree.iterparse(handle, events=("start", "end")):
            if (event == 'start') and (element.tag == 'row'):
                keys = {}
                fields = {}
                row_operation = element.attrib.get( 'operation', 'any' )
            elif (event == 'end') and (element.tag == 'row'):
                element.clear()
                if ( ( for_operation == 'any' ) or 
                     ( row_operation == 'any' ) or 
                     ( for_operation == row_operation ) ):
                    yield keys, fields
            elif (event == 'end') and (element.tag.lower() == 'resultset'):
                return
            elif (event == 'end'):
                is_key = element.attrib.get('isPrimaryKey', 'false').lower()
                if (element.tag in pkeys) or (is_key == 'true'):
                    is_key = 'true'
                value = StandardXML.Convert_Field_To_Value(element)
                if (is_key == 'true'):
                    keys[element.tag] = value
                else:
                    fields[element.tag] = value
        return

    @staticmethod
    def Filter_Rows(rfile, wfile, callback=None):
        wfile.seek(0)
        rfile.seek(0)
        table_name = None
        format_name = None
        format_class = None
        for event, element in etree.iterparse(rfile, events=("start",)):
            if (event == 'start' and element.tag == 'ResultSet'):
                table_name   = element.attrib.get('tableName')
                format_name  = element.attrib.get('formatName')
                format_class = element.attrib.get('className')
                element.clear()
                break
        wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        wfile.write(u'<ResultSet formatName="{0}" className="{1}" tableName="{2}">'.\
            format(format_name, format_class, table_name))
        rfile.seek(0)
        for event, element in etree.iterparse(rfile, events=("end",)):
            if (event == 'end') and (element.tag == 'row'):
                if (callback is not None):
                    if (callback(element)):
                        wfile.write(etree.tostring(element))
                else:
                    wfile.write(etree.tostring(element))
                element.clear()
            elif (event == 'end') and (element.tag == 'ResultSet'):
                wfile.write(u'</ResultSet>')
                break
