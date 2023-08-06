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
from StringIO            import StringIO
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from utility             import sql_connect
from command             import SQLCommand

class UpdateAction(ActionCommand, SQLCommand):
    #TODO: Needs doCommit support
    __domain__    = "action"
    __operation__ = "sql-update"
    __aliases__   = [ 'sqlUpdate', 'sqlUpdateAction' ]

    def __init__(self):
        ActionCommand.__init__( self )

    def do_action(self):
        db = sql_connect( self._source )
        cursor = db.cursor( )
        summary = StringIO( u'' )
        table, format_name, format_class = self._read_result_metadata( self.rfile )
        summary.write( u'Update target is table "{0}"\n'.format( table ) )
        counter = 0
        # TODO: Convert to use iterparse! (Issue#40)
        # TODO: This does nothing with the "primaryKeys" specified in the action parameters
        try:
            for keys, fields in self._read_rows(self.rfile, [], for_operation = 'update' ):
                if not fields:
                    continue
                if not keys:
                    raise CoilsException( 'No primary keys provided for update of SQL record.' )
                sql, values = self._create_update_from_fields( db, table, keys, fields )
                try:
                    cursor.execute( sql, values )
                except Exception, e:
                    self.log_message( 'FAILED SQL: {0} VALUES: {1}'.format( unicode( sql ), unicode( values ) ),
                                      category='error')
                    raise e
                counter += 1
            if self._commit == 'YES':
                db.commit( )
        except Exception, e:
            raise e
        finally:
            summary.write( u'{0} records processed.'.format( counter ) )
            self.log_message( summary.getvalue( ), category='error' )
            summary = None
            cursor.close( )
            db.close( )

    def parse_action_parameters(self):
        self._source = self.action_parameters.get( 'dataSource', None )
        self._keys   = self.action_parameters.get( 'primaryKeys', '' ).split( ',' )
        self._commit = self.action_parameters.get( 'commit', 'YES' ).upper( )

        if self._source is None:
            raise CoilsException( 'No source defined for selectAction' )

    def do_epilogue(self):
        pass
