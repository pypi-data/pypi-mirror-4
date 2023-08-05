#!/usr/bin/python
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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetProjectTaskActions(GetCommand):
    __domain__ = "project"
    __operation__ = "get-task-actions"

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        self._limit = params.get('limit', 150)
        if ('id' in params):
            self.project = self.get_by_id(params.get('id'))
        elif ('project' in params):
            self.project = params['project']
        else:
            self.project = None

    def get_by_id(self, object_id):
        project = self._ctx.run_command('project::get', id=int(object_id))
        if (project is None):
            raise CoilsException('Unable to retrieve task actions for specified project')
        return project


    def run(self, **params):
        self.access_check = False
        self.mode = RETRIEVAL_MODE_MULTIPLE
        db = self._ctx.db_session()
        if (self.project is None):
            inner_query = db.query(Project.object_id).join(ProjectAssignment).\
                             filter(and_(ProjectAssignment.child_id.in_(self._ctx.context_ids),
                                          Project.status != 'archived')).\
                             subquery()

            query = db.query(TaskAction).\
                       join(Task, Task.notes).\
                       filter(Task.project_id.in_(inner_query)).\
                       order_by(TaskAction.date.desc()).limit(self._limit)
        else:
            print 'project actions'
            query = db.query(TaskAction).\
                       join(Task, Task.notes).\
                       filter(Task.project_id == self.project.object_id).\
                       order_by(TaskAction.date.desc()).limit(self._limit)
        self.set_return_value(query.all())
