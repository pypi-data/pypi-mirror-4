#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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

class RevertArchivedLoginValues(ActionCommand):
    # TODO: Support receiving an account representation as an input message
    __domain__ = "action"
    __operation__ = "revert-archived-login-values"
    __aliases__   = [ 'revertArchivedLoginValues', "revertArchivedLoginValuesAction" ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def mimetype(self):
        return 'text/plain'

    def do_action(self):
        if (self._ctx.is_admin):
            # TODO: Move this to a Logic command
            query = self._ctx.db_session().query(Contact).filter(Contact.status == 'archived')
            for contact in query.all():
                login = 'OGo{0}'.format(contact.object_id)
                if contact.login != login:
                    self._ctx.run_command('contact::set', object=contact, values={ 'login': login } )
                    self.wfile.write(u'Modified login of contactId#{0}'.format(contact.object_id))
        else:
            raise CoilsException('Insufficient privilages to invoke removeAccountStatusAction')

    def parse_action_parameters(self):
        pass
