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
from coils.core import *

class SetDefaults(Command):
    __domain__ = "account"
    __operation__ = "set-defaults"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        self.login = None
        if ('defaults' in params):
            self.defaults = params('defaults')
        else:
            raise CoilsException('No defaults provided to {0}'.format(self.command_name()))
        if (('id' in params) or ('login' in params)):
            if ('id' in params):
                self.account_id = int(params['id'])
            else:
                self.login = params['login']
        else:
            self.account_id = self._ctx.account_id

    def run(self):
        self._result = None
        if (self.login is not None):
            account = self._ctx.run_command('account::get', login=self.login)
            if (account is None):
                raise CoilsException('{0} unable to resolve login {1}'.format(self.command_name(), self.login))
            self.account_id = account.object_id
        if ((account.object_id not in (self._ctx.context_ids)) or
            (self._ctx.account_id > 10000)):
            raise CoilsException('Account {0} not permitted to modify defaults of account {1}'.format(self._ctx.account_id, self.account_id))
        ud = UserDefaultsManager(self.account_id)
        ud.update_defaults(self.defaults)
        ud.sync()
