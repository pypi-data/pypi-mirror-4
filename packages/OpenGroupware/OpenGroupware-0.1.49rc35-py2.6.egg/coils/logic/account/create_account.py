#
# Copyright (c) 2009, 2012
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
from datetime         import datetime, timedelta
from pytz             import timezone
from sqlalchemy       import *
from sqlalchemy.orm   import *
from coils.foundation import *
from coils.core       import *
from keymap           import COILS_ACCOUNT_KEYMAP

class CreateAccount(Command):
    __domain__ = "account"
    __operation__ = "new"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self.login       = params.get( 'login', None )
        self.password    = params.get( 'password', None )
        self.template_id = long( params.get( 'template_id', 9999 ) )
        self.obj         = params.get( 'contact', None )

        if not self.login:
            raise CoilsException( 'No login value specified for new account' )

        if not self.obj:
            raise CoilsException( 'No "contact" provided to account::new' )

        if not isinstance( self.obj, Contact ):
            raise CoilsException( 'Contact provided to account::new is not a contact entity, type is {0}'.format( type( self.obj ) ) )

    def check_run_permissions(self):
        if self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN  ):
            return
        raise AccessForbiddenException( 'Context lacks administrative role; cannot create teams.' )

    def run(self):
        # TODO: Verify that the template_id provided identifies a real entity?
        if not self.obj.is_account:
            self.obj.is_account = 1
            self.obj.template_user_id = self.template_id
            self.obj.login = self.login
            if self.password:
                self._ctx.run_command( 'account::set-password', login=self.obj.login, password=self.password )
        else:
            raise CoilsException( 'OGo#{0} [Contact] is already an account'.format( self.obj.object_id ) )
