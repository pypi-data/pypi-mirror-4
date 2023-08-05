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
from coils.foundation import diff_id_lists, Contact, Enterprise, ProjectAssignment
from command          import ProjectCommand


class SetProjectEnterprises(Command, ProjectCommand):
    __domain__      = "project"
    __operation__   = "set-enterprises"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('project' in params):
            self._project_id = params.get('project').object_id
        elif ('project_id' in params):
            self._project_id = int(params.get('project_id'))
        else:
            raise CoilsException('No project specified for project::set-enterprises')
        self._enterprise_ids = []
        if ('enterprises' in params):
            for assignment in params.get('enterprises'):
                self._enterprise_ids.append(int(assignment.object_id))
        elif ('enterprise_ids' in params):
            self._enterprise_ids = [int(o) for o in params.get('enterprise_ids')]

    def run(self):
        # TODO: Check access to contact_id
        db = self._ctx.db_session()
        # Get list of enterprse ids project is assigned to
        query = db.query(ProjectAssignment).filter(ProjectAssignment.parent_id == self._project_id)
        assigned_to = [int(o.child_id) for o in query.all()]
        print '  Assigned: {0}'.format(assigned_to)
        assigned_to = self._ctx.type_manager.filter_ids_by_type(assigned_to, 'Enterprise')
        # Diff the new and the old lists
        print '  Assigned: {0}'.format(assigned_to)
        print '  Enterprises: {0}'.format(self._enterprise_ids)
        inserts, deletes = diff_id_lists(self._enterprise_ids, assigned_to)
        print ' ENTERPRISE ASSIGNMENTS '
        print '  Insert: {0}'.format(inserts)
        print '  Delete: {0}'.format(deletes)
        print
        assigned_to = None
        query = None
        # Perform sync
        if (len(inserts) > 0):
            for enterprise_id in inserts:
                db.add(ProjectAssignment(self._project_id, enterprise_id))
        if (len(deletes) > 0):
            db.query(ProjectAssignment).\
                filter(and_(ProjectAssignment.child_id.in_(deletes),
                             ProjectAssignment.parent_id == self._project_id)).\
                delete(synchronize_session='fetch')
