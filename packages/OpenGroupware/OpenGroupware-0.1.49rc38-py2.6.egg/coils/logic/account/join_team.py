#
# Copyright (c) 2012, 2013
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
# THE SOFTWARE.
#
from sqlalchemy         import *
from coils.core         import *

class JoinTeam(Command):
    __domain__ = "account"
    __operation__ = "join-team"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._account = params.get( 'account', None )
        self._team    = params.get( 'team', None )
        if not self._account:
            raise CoilsException( 'No account specified to join team' )
        if not isinstance(self._account, Contact):
            raise CoilsException( '"account" is not a Contact object.' )
        if not self._account.is_account:
            raise CoilsException( 'Specified Contact object is not an account' )
        if not self._team:
            raise CoilsException( 'No team specified for account to join or leave' )
        if not isinstance( self._team, Team ):
            raise CoilsException( '"team" is not a Team object.' )            

    def check_run_permissions(self):
        if self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN ):
            return
        raise  AccessForbiddenException( 'Context lacks administrative role; cannot join an account to a team' )

    def run(self):
        self._result = []
        db = self._ctx.db_session()
        # Does this assignment already exist?
        query = db.query( CompanyAssignment ).filter( and_( CompanyAssignment.parent_id == self._team.object_id,
                                                            CompanyAssignment.child_id == self._account.object_id ) )
        result = query.all( )
        if not result:
            db.add( CompanyAssignment( self._team.object_id, self._account.object_id ) )
            self.set_return_value( True )
            return
        self.set_return_value( False )
            
class LeaveTeam(JoinTeam):
    __domain__ = "account"
    __operation__ = "leave-team"
    mode = None            
            
    def run(self):
        self._result = []
        db = self._ctx.db_session()
        # Does this assignment already exist?
        query = db.query( CompanyAssignment ).filter( and_( CompanyAssignment.parent_id == self._team.object_id,
                                                            CompanyAssignment.child_id == self._account.object_id ) )
        result = query.all( )
        if result:
            db.delete( result[ 0 ] )
            self.set_return_value( True )
            return
        self.set_return_value( False )
