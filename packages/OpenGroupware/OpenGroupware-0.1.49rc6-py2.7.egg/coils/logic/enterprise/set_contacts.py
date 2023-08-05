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
from command          import EnterpriseCommand

class SetContacts(Command, EnterpriseCommand):
    __domain__      = "enterprise"
    __operation__   = "set-contacts"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('enterprise' in params):
            self._enterprise_id = params.get('enterprise').object_id
        elif ('enterprise_id' in params):
            self._enterprise_id = int(params.get('enterprise_id'))
        else:
            raise CoilsException('No enterprise specified for enterprise::set-contacts')
        self._contact_ids = []
        if ('contacts' in params):
            for assignment in params.get('contacts'):
                self._contact_ids.append(int(assignment.object_id))
        elif ('contact_ids' in params):
            self._contact_ids = [int(o) for o in params.get('contact_ids')]

    def run(self):
        # TODO: Check access to contact_id
        db = self._ctx.db_session()
        # Get list of project ids company is assigned to
        query = db.query(CompanyAssignment).filter(CompanyAssignment.parent_id == self._enterprise_id)
        assigned_to = [int(o.child_id) for o in query.all()]
        # Remove Team Ids! (Team assignments are also Company Assignments)
        assigned_to = self._ctx.type_manager.filter_ids_by_type(assigned_to, 'Contact')
        # Diff the new and the old lists
        inserts, deletes = diff_id_lists(self._contact_ids, assigned_to)
        assigned_to = None
        query = None
        # Perform sync
        if (len(inserts) > 0):
            for contact_id in inserts:
                db.add(CompanyAssignment(self._enterprise_id, contact_id))
        if (len(deletes) > 0):
            db.query(CompanyAssignment).\
                filter(and_(CompanyAssignment.parent_id == self._enterprise_id,
                             CompanyAssignment.child_id.in_(deletes))).\
                delete(synchronize_session='fetch')
