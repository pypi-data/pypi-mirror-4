#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy       import and_
from coils.core       import *
from coils.foundation import Contact, ProjectAssignment

class AssignCompanyToProject(Command):
    __domain__      = "project"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):

        Command.parse_parameters(self, **params)

        if 'project' in params:
            self._project_id = parans.get('project').object_id
        elif 'project_id' in params:
            self._project_id = int(params.get('project_id'))
        else:
            raise CoilsException('No project specified for project::assign-contact')

    def run(self):
        # TODO: Check access to contact_id
        db = self._ctx.db_session()
        # Get list of project ids company is assigned to
        query = db.query(ProjectAssignment).filter(and_( ProjectAssignment.parent_id == self._project_id,
                                                         ProjectAssignment.child_id == self._company_id ) )
        if query.all():
            self.set_result_value(False)
        else:
            db.add(ProjectAssignment(project_id, self._company_id))
            self.set_result_value(True)


class AssignContactToProject(AssignCompanyToProject):
    __operation__   = "assign-contact"

    def parse_parameters(self, **params):
        AssignCompanyToProject.parse_parameters(self, **params)

        if 'contact' in params:
            self._company_id = params.get('contact').object_id
        elif 'contact_id' in params:
            self._company_id = int(params.get('contact_id'))
        else:
            raise CoilsException('No contact specified for project::assign-contact')


class AssignEnterpriseToProject(AssignCompanyToProject):
    __operation__   = "assign-enterprise"

    def parse_parameters(self, **params):
        AssignCompanyToProject.parse_parameters(self, **params)

        if 'enterprise' in params:
            self._company_id = params.get('enterprise').object_id
        elif 'enterprise_id' in params:
            self._company_id = int(params.get('enterprise_id'))
        else:
            raise CoilsException('No enterprise specified for project::assign-enterprise')
