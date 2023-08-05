#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy       import *
from coils.core       import *
from coils.foundation import CompanyAssignment
from command          import ContactCommand

class GetEnterprises(Command):
    __domain__      = "contact"
    __operation__   = "get-enterprises"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters( self, **params )
        x = params.get( 'contact', params.get( 'object', None ) )
        print x
        if x:
            self._contact_id = x.object_id
        else:
            self._contact_id = int( params.get( 'contact_id', 0 ) )
        if not self._contact_id:
            raise CoilsException( 'No contact specified for contact::get-enterprises' )

    def run(self):
        # TODO: Check access to contact_id
        db = self._ctx.db_session( )
        query = db.query( CompanyAssignment ).filter( CompanyAssignment.child_id == self._contact_id )
        assigned_to = [ int( o.parent_id ) for o in query.all( ) ]
        self.set_return_value( self._ctx.run_command( 'enterprise::get', ids = assigned_to ) )
