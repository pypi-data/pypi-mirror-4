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
import os, base64
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render


class GetEntityAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "get-entity"
    __aliases__   = [ 'getEntityAction', 'getEntity' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        kind = self._ctx.type_manager.get_type(self._id).lower()
        if (kind == 'Unknown'):
            raise CoilsException('Cannot retrieve entity of Unknown type.')
        entity = self._ctx.run_command('{0}::get'.format(kind), id=int(self._id))
        if (entity is None):
            raise CoilsException('Failed to retrieve objectId#{0} via {1}::get.'.format(self._id, kind))
        results = XML_Render.render(entity, self._ctx)
        self.wfile.write(results)

    @property
    def result_mimetype(self):
        return 'application/xml'

    def parse_action_parameters(self):
        self._id     = self.action_parameters.get('objectId', None)
        if (self._id is None):
            self._id = self._ctx.account_id
        else:
            self._id = self.process_label_substitutions(self._id)

    def do_epilogue(self):
        pass
