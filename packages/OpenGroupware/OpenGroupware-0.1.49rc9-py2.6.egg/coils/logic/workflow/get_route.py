#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from utility            import filename_for_route_markup

class GetRoute(GetCommand):
    __domain__ = "route"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        # WARN: If you specify id/ids parameters, name is ignored
        if (self.query_by is None):
            if ('name' in params):
                self.mode = 1
                self.query_by = 'name'
                self.name = params['name'].lower()

    def add_route_markup(self, routes):
        for route in routes:
            handle = BLOBManager.Open(filename_for_route_markup(route), 'rb', encoding='binary')
            if (handle is not None):
                bpml = handle.read()
                route.set_markup(bpml)
                BLOBManager.Close(handle)
            else:
                route.set_markup('')
        return routes

    def run(self, **params):
        db = self._ctx.db_session()
        if (self.query_by == 'object_id'):
            if (len(self.object_ids) > 0):
                query = db.query(Route).filter(and_(Route.object_id.in_(self.object_ids),
                                                     Route.status != 'archived'))
        elif (self.query_by == 'name'):
            #query = db.query(Route).filter(and_(Route.name==self.name,
            #                                     Route.status != 'archived'))
            query = db.query(Route).filter(and_(func.lower(Route.name).like(self.name),
                                                Route.status != 'archived'))
        else:
            self.mode = 2
            query = db.query(Route)
        self.set_return_value(self.add_route_markup(query.all()))
        