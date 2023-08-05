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

class GetTombstone(GetCommand):
    __domain__ = "object"
    __operation__ = "get-tombstone"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.object_ids = []
        if ('id' in params):
            self.set_single_result_mode()
            self.object_ids.append(int(params['id']))
        elif ('ids' in params):
            self.set_multiple_result_mode()
            self.object_ids.extend([int(x) for x in params['ids']])
        else:
            raise CoilsException('No id or ids specified for object::get-tombstone')

    def run(self):
        self.disable_access_check()
        db = self._ctx.db_session()
        query = db.query(AuditEntry).filter(and_(AuditEntry.context_id.in_(self.object_ids),
                                                 AuditEntry.action=='99_delete'))
        result = query.all()
        print result
        self.set_return_value(result)
