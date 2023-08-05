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

class RemoveAccountMembershipAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "remove-account-membership"
    __aliases__   = [ 'removeAccountMembership', "removeAccountMembershipAction" ]

    def __init__(self):
        ActionCommand.__init__(self)

    def _get_object_id_from_input(self):
        doc = etree.parse(self.rfile)
        return int(doc.getroot().get('objectId'))

    def do_action(self):
        if (self._ctx.is_admin):
            if (self._user_id is None):
                self._user_id = self._get_object_id_from_input()
            account = self._ctx.run_command('contact::get', id=self._user_id,
                                                            include_archived=True)
            result = self._ctx.run_command('account::remove-membership', account_id=self._user_id)
            self.wfile.write(u'Removed {0} Team assignments.\n'.format(result[0]))
            self.wfile.write(u'Removed {0} Enterprise assignments.\n'.format(result[1]))
            self.wfile.write(u'Removed {0} Project assignments.\n'.format(result[2]))
        else:
            raise CoilsException('Insufficient privilages to invoke removeAccountMembershipAction')

    def parse_action_parameters(self):
        self._user_id = self.action_parameters.get('objectId', None)
        if (self._user_id is not None):
            self._login = int(self.process_label_substitutions(self._login))
