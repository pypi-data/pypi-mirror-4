#
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

class RemoveMembership(Command):
    __domain__ = "account"
    __operation__ = "remove-membership"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._user_id = int(params.get('account_id'))

    def run(self):
        self._result = []
        db = self._ctx.db_session()
        # Teams
        query = db.query(Team, CompanyAssignment).filter(and_(Team.object_id == CompanyAssignment.parent_id,
                                                               CompanyAssignment.child_id == self._user_id))
        teams = []
        assignments = []
        for result in query.all():
            if result[0].object_id not in teams:
                teams.append(result[0].object_id)
            assignments.append(result[1].object_id)
        if (len(teams) > 0):
            for team in db.query(Team).filter(Team.object_id.in_(teams)).all():
                team.version = team.version + 1
                self.log.debug('Removing assignment to Team id#{0} from account id#{1}'.format(team.object_id, self._user_id))
            count = db.query(CompanyAssignment).\
                        filter(CompanyAssignment.object_id.in_(assignments)).\
                        delete(synchronize_session='fetch')
            self.log.debug('{0} team assignments deleted'.format(count))
            self._result.append(count)
        else:
            self._result.append(0)
        # Enterprises
        query = db.query(Enterprise, CompanyAssignment).filter(and_(Enterprise.object_id == CompanyAssignment.parent_id,
                                                                     CompanyAssignment.child_id == self._user_id))
        enterprises = []
        assignments = []
        for result in query.all():
            if result[0].object_id not in enterprises:
                enterprises.append(result[0].object_id)
            assignments.append(result[1].object_id)
        if (len(enterprises) > 0):
            for enterprise in db.query(Enterprise).filter(Enterprise.object_id.in_(enterprises)).all():
                enterprise.version = enterprise.version + 1
                self.log.debug('Removing assignment to Enterprise id#{0} from account id#{1}'.format(enterprise.object_id, self._user_id))
            count = db.query(CompanyAssignment).\
                        filter(CompanyAssignment.object_id.in_(assignments)).\
                        delete(synchronize_session='fetch')
            self.log.debug('{0} enterprise assignments deleted'.format(count))
            self._result.append(count)
        else:
            self._result.append(0)
        # Projects
        query = db.query(Project, ProjectAssignment).filter(and_(Project.object_id == ProjectAssignment.parent_id,
                                                                  ProjectAssignment.child_id == self._user_id))
        projects = []
        assignments = []
        for result in query.all():
            if result[0].object_id not in projects:
                projects.append(result[0].object_id)
            assignments.append(result[1].object_id)
        if (len(projects) > 0):
            for project in db.query(Project).filter(Project.object_id.in_(projects)).all():
                project.version = project.version + 1
                self.log.debug('Removing assignment to Project id#{0} from account id#{1}'.format(project.object_id, self._user_id))
            count = db.query(ProjectAssignment).\
                        filter(ProjectAssignment.object_id.in_(assignments)).\
                        delete(synchronize_session='fetch')
            self.log.debug('{0} project assignments deleted'.format(count))
            self._result.append(count)
        else:
            self._result.append(0)
