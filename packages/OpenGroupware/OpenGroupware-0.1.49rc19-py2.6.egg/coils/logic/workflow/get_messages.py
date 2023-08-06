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

class GetMessages(GetCommand):
    __domain__ = "process"
    __operation__ = "get-messages"

    def __init__(self):
        GetCommand.__init__(self)
        self.set_multiple_result_mode()

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('pid' in params):
            self.pid = params['pid']
            self.query_by = 'pid'
        elif ('process' in params):
            self.pid = params['process'].object_id
            self.query_by = 'pid'

    def get_process(self, pid):
        if (isinstance(pid, Process)):
            return pid
        return self._ctx.run_command('process::get', id=pid, access_check=self.access_check)

    def run(self, **params):
        db = self._ctx.db_session()
        if (self.pid is None):
            raise CoilsException('No PID specified for process::get-messages')
        process = self.get_process(self.pid)
        if (process is None):
            self.set_return_value([])
            return
            raise CoilsException('Unable to resolve PID {0}'.format(self.pid))
        query = db.query(Message).filter(Message.process_id==process.object_id)
        self._result = []
        self.set_return_value(query.all())
