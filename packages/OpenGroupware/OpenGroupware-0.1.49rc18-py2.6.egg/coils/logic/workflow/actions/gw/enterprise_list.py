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
import os
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render


class EnterpriseList(ActionCommand):
    __domain__ = "action"
    __operation__ = "list-enterprises"
    __aliases__   = [ 'listEnterprises', 'listEnterprisesAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        result = self._ctx.run_command('enterprise::list',
                                       contexts=[self._context_id],
                                       properties=[Enterprise],
                                       limit=self._limit)
        XML_Render.render(result, self._ctx, detail_level=self._detail,
                                             stream=self.wfile)

    @property
    def result_mimetype(self):
        return 'application/xml'

    def parse_action_parameters(self):
        self._detail     = int(self.action_parameters.get('detailLevel', 65503))
        self._context_id = self.action_parameters.get('contextId', self._ctx.account_id)
        self._context_id = self.process_label_substitutions(self._context_id)
        self._context_id = int(self._context_id)
        self._limit      = int(self.action_parameters.get('limit', 65535))

    def do_epilogue(self):
        pass
