#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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

class GetTeam(GetCommand):
    __domain__ = "team"
    __operation__ = "get"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if ('member_id' in params):
            self.query_by = 'membership'
            self.set_multiple_result_mode()
            self.object_ids.append(int(params['member_id']))
        elif ('email' in params):
            self.query_by = 'email'
            self.set_multiple_result_mode()
            self._email = params['email'].lower()
        elif ('name' in params):
            self.query_by = 'name'
            self.set_single_result_mode()
            self._name = params['name']

    def run(self):
        db = self._ctx.db_session()
        if (self.query_by == 'object_id'):
            query = db.query(Team).filter(Team.object_id.in_(self.object_ids))
        elif (self.query_by == 'membership'):
            query = db.query(Team)
            query = query.join(CompanyAssignment)
            query = query.filter(CompanyAssignment.child_id.in_(self.object_ids))
        elif (self.query_by == 'email'):
            query = db.query(Team).filter(Team.email.ilike(self._email))
        elif (self.query_by == 'name'):
            query = db.query(Team).filter(Team.name.ilike(self._name))
        else:
            # Default action is to retrieve all teams
            self.set_multiple_result_mode()
            query = db.query(Team)
        # Access check *MUST* be disabled or you end up in an infinite recursion; this is because
        # team membership needs to be known to determine administrative priviliges and the access
        # manager logic checks if the context has administrative privileges
        self.disable_access_check()
        self.set_return_value(query.all())
