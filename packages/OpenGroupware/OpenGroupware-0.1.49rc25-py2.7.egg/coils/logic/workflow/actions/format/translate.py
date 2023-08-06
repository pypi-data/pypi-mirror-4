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
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.logic.workflow.tables import Table

class TranslateAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "translate"
    __aliases__   = [ 'translateAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        if not self._value:
            self._value = self.rfile.read( )
        result = self._table.lookup_value( [ self._value, ] )
        if result:
            self.wfile.write( unicode( result ) )
        else:
            self.wfile.write( u'' )

    def parse_action_parameters(self):
        self._value  = self.action_parameters.get( 'value', None )
        if self._value:
            self._value = unicode( self._value )
            self._value = self.process_label_substitutions( self._value )
        
        table_name = self.action_parameters.get('tableName', None )
        if table_name:
            table = Table.Load( table_name )
            if table:
                try:
                    table.setup( context = self._ctx, process=self.process, scope=self.scope_stack )
                except Exception, e:
                    self.log.error( 'Unable to setup Table "{0}" for translateAction'.format( table_name ) )
                    raise e
            else:
                self.log.error( 'Unable to marshal Table "{0}" for translateAction'.format( table_name ) )
                raise CoilsException( 'Unable to marshal Table "{0}" for translateAction'.format( table_name ) )
        else:
            raise CoilsException( 'No tableName specified for translateAction' )
        self._table = table

    def do_epilogue(self):
        pass
