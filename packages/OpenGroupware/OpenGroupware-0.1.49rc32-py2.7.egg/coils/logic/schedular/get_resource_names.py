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
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetResourceNames(GetCommand):
    __domain__ = "resource"
    __operation__ = "get-names"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def run(self):
        db = self._ctx.db_session()
        if (len(self.object_ids)):
            query = db.query(Resource).filter(and_(Resource.object_id.in_(self.object_ids),
                                                    Resource.status != 'archived'))
        else:
            query = db.query(Resource).filter(Resource.status != 'archived')
        if (self.access_check):
            data = self._ctx.access_manager.filter_by_access('r', query.all())
        else:
            data = query.all()
        self._result = [ ]
        if (len(data) > 0):
            for r in data:
                self._result.append(r.name)
        return