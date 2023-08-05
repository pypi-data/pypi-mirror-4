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
from sqlalchemy          import *
from coils.core          import *
from coils.foundation    import Contact
from crypt               import crypt
import random        

#TODO: Allow administrators to overwrite the defaults of other users.
#TODO: Store defaults

class SetPassword(Command):
    __domain__ = "account"
    __operation__ = "set-password"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        self.password = params.get('password', None)
        self.login = params.get('login', self._ctx.get_login())

    def generate_salt(self):
        salt = ''
        while (len(salt) < 2):
            i = random.randrange(1024)
            if (i < 257):
                x = chr(random.randrange(256))
                if (x.isalnum()):
                    salt = '{0}{1}'.format(salt, x)
        return salt

    def run(self, **params):
        self._result = False
        if (self.password is None):
            raise CoilsException('No password specified')
        db = self._ctx.db_session()
        query = db.query(Contact).filter(and_(Contact.login==self.login,
                                               Contact.is_account==1,
                                               Contact.status!='archived'))
        data = query.all()
        if ( len(data) > 1 ):
            raise AuthenticationException('Multiple accounts match criteria!')
        elif ( len(data) == 0 ):
            self.log.error('No such account as {0}.'.format(self.login))
            raise CoilsException('No such account as {0}.'.format(self.login))
        else:
            account = data[0]
            account.password = crypt(self.password, self.generate_salt())
            self._result = True