#
# Copyright (c) 2013 Adam Tauno Williams <awilliam@whitemice.org>
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

class GetRouteGroup(GetCommand):
    __domain__ = "routegroup"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        # WARN: If you specify id/ids parameters, name is ignored
        if (self.query_by is None):
            if ('name' in params):
                self.mode = 1
                self.query_by = 'name'
                self.name = params['name'].lower()

    def run(self, **params):
        db = self._ctx.db_session()
        if self.query_by == 'object_id' and self.object_ids:
            query = db.query( RouteGroup ).filter( RouteGroup.object_id.in_( self.object_ids ) )
        elif self.query_by == 'name':
            query = db.query( RouteGroup ).filter( func.lower( RouteGroup.name ).like( self.name ) )
        else:
            self.mode = 2
            query = db.query( RouteGroup )
        if query:
            results = query.all( )
            self.set_return_value( results )
        else:
            self.set_return_value( [ ] )
