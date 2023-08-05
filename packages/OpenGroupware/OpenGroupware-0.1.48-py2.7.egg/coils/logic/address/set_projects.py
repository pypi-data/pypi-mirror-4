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
from sqlalchemy       import *
from coils.core       import *
from coils.foundation import diff_id_lists


class SetProjects(Command):
    __domain__      = "company"
    __operation__   = "set-projects"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('company' in params):
            self._company_id = params.get('company').object_id
        elif ('company_id' in params):
            self._company_id = int(params.get('company_id'))
        else:
            raise CoilsException('No company specified for action::set-projects')
        self._project_ids = []
        if ('projects' in params):
            for assignment in params.get('projects'):
                self._project_ids.append(int(assignment.parent_id))
        elif ('project_ids' in params):
            self._project_ids = [int(o) for o in params.get('project_ids')]

    def run(self):
        db = self._ctx.db_session()
        # Get list of project ids company is assigned to
        query = db.query(ProjectAssignment).filter(ProjectAssignment.child_id == self._company_id)
        assigned_to = [int(o.parent_id) for o in query.all()]
        inserts, deletes = diff_id_lists(self._project_ids, assigned_to)
        assigned_to = None
        query = None
        if (len(inserts) > 0):
            for project_id in inserts:
                x = ProjectAssignment(project_id, self._company_id)
                db.add(x)
        if (len(deletes) > 0):
            db.query(ProjectAssignment).\
                filter(and_(ProjectAssignment.parent_id.in_(deletes),
                             ProjectAssignment.child_id == self._company_id)).delete(synchronize_session='fetch')
