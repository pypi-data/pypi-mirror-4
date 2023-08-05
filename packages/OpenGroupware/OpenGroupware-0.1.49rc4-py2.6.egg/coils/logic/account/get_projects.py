#
# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core.logic import GetCommand

class GetProjects(GetCommand):
    __domain__ = "account"
    __operation__ = "get-projects"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self.kinds = None
        self.parents_only = params.get('parents_only', False)
        if ('kind' in params):
            self.kinds = [ params.get('kind').strip() ]
        elif ('kinds' in params):
            x = params.get('kinds')
            if isinstace(x, basestring):
                x = x.split(',')
            if isinstance(x, list):
                for k in x:
                    self.kinds.append(k.strip())
            else:
                raise CoilsException('Unable to parse command parameter "kinds".')

    def run(self):
        db = self._ctx.db_session()
        self.mode = 2
        if (len(self.object_ids) == 0):
            self.object_ids.extend(self._ctx.context_ids)
        query = db.query(Project)
        query = query.join(ProjectAssignment)
        if (self.kinds is None):
            if self.parents_only:
                query = query.filter(and_(ProjectAssignment.child_id.in_(self.object_ids),
                                          Project.parent_id == None,
                                          Project.status != 'archived'))
            else:
                query = query.filter(and_(ProjectAssignment.child_id.in_(self.object_ids),
                                          Project.status != 'archived'))
        else:
            if self.parents_only:
                 query = query.filter(and_(ProjectAssignment.child_id.in_(self.object_ids),
                                           Project.kind.in_(self.kinds),
                                           Project.parent_id == None,
                                           Project.status != 'archived'))
            else:
                query = query.filter(and_(ProjectAssignment.child_id.in_(self.object_ids),
                                          Project.kind.in_(self.kinds),
                                          Project.status != 'archived'))
        self.set_return_value(query.all())
