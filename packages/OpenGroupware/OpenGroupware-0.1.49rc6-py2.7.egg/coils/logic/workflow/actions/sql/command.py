#
# Copyright (c) 2010, 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
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
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.logic.workflow.formats import Format
from utility             import sql_connect

class SQLCommand(object):
    """ Parent class, used as a mix-in, by SQL related Workflow actions; so these will
        be mixed-in with an ActionCommand class. This class provides the methods used to
        format/type field values and construct basic SQL statements. The assumption is 
        that the input values are derived from a StandardXML row."""

    def _convert_field_to_value(self, field):
        return StandardXML.Convert_Field_To_Value( field )
        
    def _parse_row(self, row):
        fields = {}
        keys   = {}
        #self.log.error(etree.tostring(row))
        for field in row.iterchildren():
            name  = field.tag.lower()
            # Determine if value is primary key
            is_key = field.attrib.get('isPrimaryKey', 'false').lower()
            if (name in self._keys) or (is_key == 'true'):
                is_key = 'true'
            # Process field value
            value = self._convert_field_to_value(field)
            # Set as key or value
            if (is_key == 'true'):
                keys[name] = value
            else:
                fields[name] = value
        #self.log.error('ROW KEYS: {0}'.format(str(keys)))
        #self.log.error('ROW FIELDS: {0}'.format(str(fields)))
        return keys, fields

    def _read_result_metadata(self, handle):
        handle.seek( 0 )
        table_name = None
        format_name = None
        format_class = None
        for event, element in etree.iterparse( handle, events=( "start", "end" ) ):
          if ( event == 'start' and element.tag == 'ResultSet' ):
            table_name   = element.attrib.get( 'tableName' )
            format_name  = element.attrib.get( 'formatName' )
            format_class = element.attrib.get( 'className' )
            break
        return table_name, format_name, format_class

    def _read_rows(self, handle, key_fields, for_operation = None):
        for keys, fields in StandardXML.Read_Rows( handle, key_fields, for_operation = for_operation ):
            yield keys, fields
        return

    def _create_update_from_fields(self, connection, table, keys, fields):
        values     = [ ]
        set_string = [ ]
        key_string = [ ]
        for i in range( 0, len( fields ) ):
            set_string.append( '{0} = {1}'.format( fields.keys( )[ i ], connection.bind_param( i + 1 ) ) )
            values.append( fields.values( )[ i ] )
        for i in range( 0, len( keys ) ):
            key_string.append( '{0} = {1}'.format( keys.keys( )[ i ], connection.bind_param( i + 1 + len( fields ) ) ) )
            values.append( keys.values( )[ i ] )
        sql = 'UPDATE {0} SET {1} WHERE {2}'.format( table,
                                                     ','.join( set_string ),
                                                     ' AND '.join( key_string ) )
        return sql, values

    def _create_insert_from_fields(self, connection, table, keys, fields):
        values = { }
        for k,v in keys.items( ):
            values[ k ] = v
        for k,v in fields.items( ):
            values[ k ] = v
        sql = 'INSERT INTO {0} ({1}) VALUES ('.format( table, ','.join( values.keys( ) ) )
        values = values.values( )
        for i in range( 0, len( values ) ):
            if ( i > 0 ):
                sql = '{0} , {1}'.format( sql, connection.bind_param( i + 1 ) )
            else:
                sql = '{0} {1}'.format( sql, connection.bind_param( i + 1 ) )
        sql = '{0})'.format( sql )
        return sql, values

    def _create_pk_select_from_keys(self, connection, table, keys):
        """ Build a SELECT statement with a WHERE clause specifying the primary keys
            identified in the StandardXML row.
            
            :param connection: The connection produced by SQLConnectionFactory.Connect
            :param table: The name of the table to SELECT from
            :param: keys: The fields comprising the primary key, may be composite.
        """
        values = [ ]
        sql = 'SELECT {0} FROM {1}'.format( ','.join( keys.keys( ) ), table )
        where = [ ]
        for i in range( 0, len( keys ) ):
            where.append( '{0} = {1}'.format( keys.keys( )[ i ], connection.bind_param( i + 1 ) ) )
            values.append( keys.values( )[ i ] )
        sql = '{0} WHERE {1}'.format( sql, ' AND '.join( where ) )
        return sql, keys.values( )

    def parse_action_parameters(self):
        """ Every SQL related action has to have a "dataSource" parameter, so this 
            parent method checks the action_parameters for that parameter. """
        self._source = self.action_parameters.get( 'dataSource', None )
        if not self._source:
            raise CoilsException( 'No source defined for selectAction' )

    def do_epilogue(self):
        pass
