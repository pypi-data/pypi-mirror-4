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
# THE SOFTWARE.
#
import os
from pytz                import timezone
from datetime            import datetime, timedelta
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render

class AcceptTaskAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "accept-task"
    __aliases__   = [ 'acceptTask', "acceptTaskAction" ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        #TODO: Support using input message as comment text (Issue#55)
        task = self._ctx.run_command('task::comment',
                                     values={ 'action': 'accept',
                                             'comment': self._comment},
                                     id=self._task_id)
        results = XML_Render.render(task, self._ctx)
        self.wfile.write(results)
        self.wfile.flush()

    def parse_action_parameters(self):
        self._comment = self.action_parameters.get('comment', None)
        self._task_id = self.action_parameters.get('taskId', self.process.task_id)
        if (self._task_id is None):
            raise CoilsException('Attempt to accept task, but no task available.')
