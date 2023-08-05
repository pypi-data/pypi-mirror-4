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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetCollection(GetCommand):
    __domain__ = "collection"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._name = params.get('name', None)

    def run(self, **params):
        db = self._ctx.db_session()
        if (self._name is not None):
            self.set_single_result_mode()
            query = db.query(Collection).filter(Collection.title == self._name)
        elif (self.query_by == 'object_id'):
            if (len(self.object_ids) > 0):
                query = db.query(Collection).filter(Collection.object_id.in_(self.object_ids))
        else:
            self.set_multiple_result_mode()
            query = db.query(Collection).filter(Collection.owner_id.in_(self._ctx.context_ids))
        #BUG: If no query was defined this will cause an error!
        self.set_return_value(query.all())
