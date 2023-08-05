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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetProjectEnterprises(GetCommand):
    __domain__ = "project"
    __operation__ = "get-enterprises"

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        if ('id' in params):
            self.project_id = int(params['id'])
        elif ('project' in params):
            self.project_id = params['project'].object_id
        elif ('object' in params):
            self.project_id = params['object'].object_id
        else:
            raise CoilsException('No project or project id provided to project::get-contacts')

    def run(self, **params):
        self.access_check = False
        self.mode = RETRIEVAL_MODE_MULTIPLE
        db = self._ctx.db_session()
        # 2010-12-23: Filter out assignments that have no child (Bug?)
        query = db.query(ProjectAssignment).filter(and_(ProjectAssignment.parent_id==self.project_id,
                                                         ProjectAssignment.child_id != None))
        object_ids = [int(entity.child_id) for entity in query.all()]
        self.set_return_value(self._ctx.run_command('enterprise::get', ids=object_ids))
