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
#
from sqlalchemy       import *
from coils.core       import *
from coils.core.logic import GetCommand

class GetProjects(GetCommand):
    __domain__ = "enterprise"
    __operation__ = "get-projects"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.kinds = None
        self.enterprise = params.get('enterprise')
        if ('kind' in params):
            self.kinds = [ params.get('kind').strip() ]
        elif ('kinds' in params):
            x = params.get('kinds')
            if (isinstace(x, basestring)):
                x = x.split(',')
            if (isinstance(x, list)):
                for k in x:
                    self.kinds.append(k.strip())
            else:
                raise CoilsException('Unable to parse command parameter "kinds".')

    def run(self):
        db = self._ctx.db_session()
        self.mode = 2
        query = db.query(Project)
        query = query.join(ProjectAssignment)
        if (self.kinds is None):
            query = query.filter(and_(ProjectAssignment.child_id == self.enterprise.object_id,
                                       Project.status != 'archived'))
        else:
            query = query.filter(and_(ProjectAssignment.child_id == self.enterprise.object_id,
                                       Project.kind.in_(self.kinds),
                                       Project.status != 'archived'))
        self.set_return_value(query.all())
