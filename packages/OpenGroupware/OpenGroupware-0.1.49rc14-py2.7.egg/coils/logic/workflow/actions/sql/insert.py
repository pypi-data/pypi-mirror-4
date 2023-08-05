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
from time                import sleep
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from utility             import sql_connect
from command             import SQLCommand

class InsertAction(ActionCommand, SQLCommand):
    #TODO: Needs doCommit support.
    __domain__    = "action"
    __operation__ = "sql-insert"
    __aliases__   = [ 'sqlInsert', 'sqlInsertAction' ]

    def __init__(self):
        ActionCommand.__init__( self )

    def do_action(self):
        db = sql_connect(self._source)
        cursor = db.cursor()
        self.log.debug( 'Reading metadata from input' )
        table_name, format_name, format_class = self._read_result_metadata(self.rfile)
        self.log_message( 'Table is "{0}"'.format( table_name ), category='info')
        counter = 0
        try:
            row_count = 0
            for keys, fields in self._read_rows( self.rfile, [], for_operation = 'insert' ):
                sql, values = self._create_insert_from_fields( db, table_name, keys, fields )
                try:
                    cursor.execute( sql, values )
                    row_count += 1
                except Exception, e:
                    message = 'error: FAILED SQL: {0} VALUES: {1}'.format( unicode( sql ), unicode( values ) )
                    self.log_message( message, category='error' )
                    raise e
                counter += 1
                if not ( counter % 1000 ):
                    sleep( 0.5 )
            self.log_message( '{0} records inserted to SQL connection'.format( row_count ),
                              category='info' )
        finally:
            cursor.close( )
            db.close( )

    def parse_action_parameters(self):
        self._source = self.action_parameters.get( 'dataSource', None )
        if self._source is None:
            raise CoilsException( 'No source defined for selectAction' )

    def do_epilogue(self):
        pass
