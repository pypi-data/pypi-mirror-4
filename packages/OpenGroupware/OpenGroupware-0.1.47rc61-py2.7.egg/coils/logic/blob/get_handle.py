#
# Copyright (c) 2010, 2012
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
# THE SOFTWARE.
#
import os
from sqlalchemy import *
from coils.core import *
from coils.core.logic import GetCommand
from command    import BLOBCommand


class GetDocumentHandle(GetCommand, BLOBCommand):
    __domain__ = "document"
    __operation__ = "get-handle"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if (len(self.object_ids) == 0):
            if ('document' in params):
                self.object_ids.append(params['document'].object_id)
        self._mode = params.get('mode', 'rb')
        self._encoding = params.get('encoding', 'binary')
        self._version  = params.get('version', None)

    def run(self, **params):
        filename = None
        db = self._ctx.db_session()
        document = self._ctx.run_command('document::get', id=self.object_ids[0])
        if (document is None):
            raise CoilsException('Unable to retrieve document entity objectId#{0}'.format(self.object_ids[0]))
        else:
            # Failure to marshall a BLOBManager will raise an exception on its own
            manager = self.get_manager(document)
            if manager:
                self._result = self.get_handle(manager, self._mode, document, version=self._version,
                                                                              encoding=self._encoding)
            else:
                self._result = None
