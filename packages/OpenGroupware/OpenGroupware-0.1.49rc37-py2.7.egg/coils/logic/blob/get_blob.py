#
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
from sqlalchemy import *
from coils.core import *
from coils.core.logic import GetCommand

class GetBLOB(GetCommand):
    __domain__ = "blob"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if (self.mode == 2):
            raise CoilsException('Multi-get mode not supported for BLOB retrieval!')
        self.version = params.get('version', 0)
        # Sink parameter may be "handle" or "data"
        self.sink = params.get('return', 'handle')

    def run(self, **params):
        db = self._ctx.db_session()
        query = db.query(Document).filter(Document.object_id.in_(self.object_ids))
        for blob in query.all():
            project = self._ctx.run_command('project::get', id=blob.project_id, access_check=False)
            if (project is not None):
                ds = blob_manager_for_project(project)
        return
