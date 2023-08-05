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
# THE SOFTWARE.
#
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render

class RemoveAccountStatusAction(ActionCommand):
    # TODO: Support receiving an account representation as an input message
    __domain__ = "action"
    __operation__ = "remove-account-status"
    __aliases__   = [ 'removeAccountStatus', "removeAccountStatusAction" ]

    def __init__(self):
        ActionCommand.__init__(self)

    def _get_object_id_from_input(self):
        try:
            doc = etree.parse(self.rfile)
        except Exception, e:
            return None
        else:
            return int(doc.getroot().get('objectId'))


    def do_action(self):
        if (self._ctx.is_admin):
            if (self._login is None):
                object_id = self._get_object_id_from_input()
                if (object_id is not None):
                    account = self._ctx.run_command('account::get', id=object_id)
                else:
                    account = None
            else:
                account = self._ctx.run_command('account::get', login=self._login)
            if (account is not None):
                if (account.is_account == 1):
                    account.is_account = 0
                    account.version += 1
                    self.log.info('account id#{0} {1} has been removed'.format(account.object_id, account.login))
                    account.login = 'OGo{0}'.format(account.object_id)
                    if (self._archive == 'YES'):
                        account.status = 'archived'
                        self.log.info('contact id#{0} has been archived'.format(account.object_id))
                    self.wfile.write(u'OK')
                else:
                    self.wfile.write(u'NOP')
            else:
                self.log.debug('Unable to retrieve account with login "{0}"'.format(self._login))
                self.wfile.write(u'FAIL')
        else:
            raise CoilsException('Insufficient privilages to invoke removeAccountStatusAction')

    def parse_action_parameters(self):
        self._login   = self.action_parameters.get('login', None)
        self._archive = self.action_parameters.get('archive', 'NO')
        if (self._login is not None):
            self._login = self.process_label_substitutions(self._login)
