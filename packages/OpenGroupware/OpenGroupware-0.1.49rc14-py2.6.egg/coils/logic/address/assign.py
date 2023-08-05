# Copyright (c) 2012
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
from sqlalchemy       import *
from coils.core       import *


class AssignCompanyObject(Command):
    __domain__      = "company"
    __operation__   = "assign"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._source = params.get( 'source' )
        self._target = params.get( 'target' )

    def check_run_permissions(self):
        if 'w' not in self._ctx.access_manager.access_rights( self._source, contexts=self.context_ids ):
            raise AccessForbiddenException( 'Insufficient access to {0}'.format( source ) )
        if 'w' not in self._ctx.access_manager.access_rights( self._target, contexts=self.context_ids ):
            raise AccessForbiddenException( 'Insufficient access to {0}'.format( source ) )

    def run(self):

        parent_id = child_id = None
        # Find the source side
        if isinstance( self._source, Team ) or isinstance( self._source, Enterprise ):
            parent_id = self._source.object_id
        elif isinstance( self._target, Team ) or isinstance( self._target, Enterprise ):
            parent_id = self._target.object_id
        # Find the target side
        if isinstance( self._source, Contact ):
            child_id = self._source.object_id
        elif isinstance( self._target, Contact ):
            child_id = self._target.object_id

        if child_id:
            if parent_id:
                db = self._ctx.db_session( )
                query = db.query( CompanyAssignment ).filter( and_( CompanyAssignment.parent_id == parent_id,
                                                                    CompanyAssignment.child_id == child_id ) )
                data = query.all( )
                if not data:
                    # TODO: What about company assignments that expire?
                    db.add( CompanyAssignment( parent_id, child_id ) )
                self.set_return_value( True )
                return

        raise CoilsException( 'Noncorresponding entity types provided to company::asign' )
