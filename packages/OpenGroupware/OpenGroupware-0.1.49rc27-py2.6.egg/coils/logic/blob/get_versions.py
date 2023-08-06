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
from coils.core.logic import GetCommand

class GetDocumentVersions(GetCommand):
    __domain__ = "document"
    __operation__ = "get-versions"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if ('document' in params):
            self.object_ids.append(params['document'].object_id)

    def run(self, **params):
        self.set_multiple_result_mode()
        db = self._ctx.db_session()
        query = db.query(DocumentVersion).filter(DocumentVersion.document_id.in_(self.object_ids))
        self.set_return_value(query.all())


class GetDocumentVersion(GetCommand):
    __domain__ = "document"
    __operation__ = "get-version"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if (len(self.object_ids) == 0):
            if ('document' in params):
                self.object_ids.append(params['document'].object_id)
            else:
                raise CoilsException('Not document id specified for document::get-version')
        self._version = int(params.get('version', 1))

    def run(self, **params):
        self.set_single_result_mode()
        object_id = self.object_ids[0]
        db = self._ctx.db_session()
        query = db.query(DocumentVersion).filter(and_(DocumentVersion.document_id == object_id,
                                                       DocumentVersion.version == self._version))
        self.set_return_value(query.all())