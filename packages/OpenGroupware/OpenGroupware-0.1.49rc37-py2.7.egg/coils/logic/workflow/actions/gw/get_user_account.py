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
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render


class GetUserAccountAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "get-user-account"
    __aliases__   = [ 'getUserAccountAction', 'getUserAccount' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        # TODO: Deal with no result by writing an empty document
        self.log.debug('Attempting to retrieve Omphalos XML representation of login "{0}"'.format(self._login))
        entity = self._ctx.run_command('account::get', login=self._login)
        if entity is not None:
            results = XML_Render.render(entity, self._ctx)
            self.wfile.write(results)
        else:
            self.log.error('Unable to retrieve Omphalos XML representation of login "{0}"'.format(self._login))

    @property
    def result_mimetype(self):
        return 'application/xml'

    def parse_action_parameters(self):
        self._login     = self.action_parameters.get('login', None)
        if (self._login is not None):
            self._login = self.process_label_substitutions(self._login)
        else:
            self._login = self._ctx.login

    def do_epilogue(self):
        pass
