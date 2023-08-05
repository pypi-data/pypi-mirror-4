# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from authenticator import Authenticator
from exception import CoilsException, AuthenticationException
from crypt  import crypt


class DBAuthenticator(Authenticator):

    def __init__(self, context, metadata, options):
        Authenticator.__init__(self, context, metadata, options)

    def authenticate(self):
        if (Authenticator.authenticate(self)):
            return
        if (self.debugging_enabled):
            self.log.debug('Verifying database password for login "{0}".'.format(self.login))
        secret = self.account.password
        if ((secret is None) and (self.account.object_id == 10000)):
            # TODO: Post waring
            self.log.warn('No password set for administrative account - permitted!')
            return True
        elif (secret is None):
            if (self.debugging_enabled):
                self.log.debug('NULL password encountered - denied.')
            raise AuthenticationException('Incorrect username or password')
        elif (secret == crypt(self.secret, secret[:2])):
            if (self.debugging_enabled):
                self.log.debug('Password verified - approved.')
            return True
        else:
            if (self.debugging_enabled):
                self.log.debug('Password incorrect - denied.')
            raise AuthenticationException('Incorrect username or password')



