#
# Copyright (c) 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy       import and_
from coils.core       import *

class AddContactProxy(Command):
    __domain__ = "account"
    __operation__ = "add-contact-proxy"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        # The user proxy rights will be granted to
        self._proxy_from = params.get( 'proxy_from', None )
        if self._proxy_from:
            if not isinstance( self._proxy_from, Contact ):
                raise CoilsException( 'Proxy-From entity is not a Contact' )
            elif not self._proxy_from.is_account:
                raise CoilsException( 'Proxy-From entity is not an account' )
        else:
            self._proxy_from = self._ctx.account_object

        # The contact the user will be able to proxy as
        self._proxy_as    = params.get( 'proxy_as', None )
        if self._proxy_as:
            if not isinstance( self._proxy_as, Contact ):
                raise CoilsException( 'Proxy-As entity is not a Contact' )
        else:
            raise CoilsException( 'Proxy-As entity not specified' )

    def check_run_permissions(self):
        # Only administrators can execute this function
        if self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN ):
            return
        raise  AccessForbiddenException( 'Context lacks administrative role; cannot join an account to a team' )

    def run(self, **params):
        db = self._ctx.db_session( )
        query = db.query( Contact ).enable_eagerloads( False )
        query = query.join( CompanyAssignment, CompanyAssignment.parent_id==Contact.object_id )
        query = query.filter( and_( CompanyAssignment.child_id  == self._proxy_from.object_id,
                                    CompanyAssignment.parent_id == self._proxy_as.object_id ) )
        if not query.all( ):
            db.add( CompanyAssignment( self._proxy_as.object_id, self._proxy_from.object_id ) )
        self.set_return_value( True )

