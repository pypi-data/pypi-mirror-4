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
from sqlalchemy import *
from coils.core import *

class RecordDocumentDownload(Command):
    __domain__ = "document"
    __operation__ = "record-download"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('document' in params):
            self.object_id = params['document'].object_id
        elif ('id' in params):
            self.object_id = int(params['id'])
        else:
            raise CoilsException('No document specified')

    def run(self, **params):
        db = self._ctx.db_session()
        obj = AuditEntry()
        obj.context_id = self.object_id
        # TODO: Add more information to the message
        obj.message    = 'document downloaded'
        obj.action     = 'download'
        obj.actor_id   = self._ctx.account_id
        db.add(obj)
