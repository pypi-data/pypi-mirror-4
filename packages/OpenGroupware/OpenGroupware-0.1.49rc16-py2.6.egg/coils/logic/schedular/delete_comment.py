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
from coils.foundation import *
from coils.core       import *

class DeleteComment(Command):
    __domain__ = "appointment"
    __operation__ = "delete-comment"

    def __init__(self):
        Command.__init__(self)
        self._result = False

    def parse_parameters(self, **params):
        self.obj = params.get('appointment', None)

    def delete(self):
        db = self._ctx.db_session()
        comment = db.query(DateInfo).filter(DateInfo.parent_id==self.obj.object_id).first()
        if (comment is not None):
            self._ctx.db_session().delete(comment)

    def run(self):
        if (self.obj is None):
            raise CoilsException('Delete comment invoked with no appointment')
        self.delete()
        self._result = True
