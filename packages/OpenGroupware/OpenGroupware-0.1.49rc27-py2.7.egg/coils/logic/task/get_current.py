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
# THE SOFTWARE.
#
from sqlalchemy       import *
from coils.foundation import *
from coils.core       import *
from coils.core.logic import GetCommand

class GetCurrentList(GetCommand):
    __domain__ = "task"
    __operation__ = "get-current"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)

    def run(self, **params):
        self.disable_access_check()
        db = self._ctx.db_session()
        self.parse_parameters(**params)
        query = db.query(Task).filter(and_(Task.state != '30_archived',
                                           or_(Task.owner_id.in_(self._ctx.context_ids),
                                               Task.executor_id != self._ctx.account_id)))
        self.set_multiple_result_mode()
        self.set_return_value(query.all())
