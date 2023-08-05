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
#
from sqlalchemy       import *
from coils.core       import *
from coils.core.logic import GetCommand

class GetProceses(GetCommand):
    __domain__ = "account"
    __operation__ = "get-processes"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._route_group = params.get('routegroup', None)

    def run(self):
        db = self._ctx.db_session()
        self.mode = RETRIEVAL_MODE_MULTIPLE
        if (len(self.object_ids) == 0):
            self.object_ids.extend(self._ctx.context_ids)
        if (self._route_group is None):
            query = db.query(Process).filter(Process.owner_id.in_(self.object_ids))
        else:
            query = db.query(Process).\
                       filter(Process.owner_id.in_(self.object_ids)).\
                       join(Route).join((ObjectProperty, ObjectProperty.parent_id == Route.object_id)).\
                       filter(and_(ObjectProperty.namespace=='http://www.opengroupware.us/oie',
                                   ObjectProperty.name=='routegroup',
                                   ObjectProperty._string_value==self._route_group))
        self.set_return_value(query.all())
