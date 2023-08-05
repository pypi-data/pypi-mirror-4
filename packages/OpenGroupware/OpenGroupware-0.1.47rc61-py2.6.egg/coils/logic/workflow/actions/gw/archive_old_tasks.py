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
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

class ArchiveOldTasksAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "archive-old-tasks"
    __aliases__   = [ 'archiveOldTasks', "archiveOldTasksAction" ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        if (self._ctx.is_admin):
            result = self._ctx.run_command('task::batch-archive', age=self._age_days)
            self.wfile.write(unicode(result))
        else:
            raise CoilsException('Insufficient privilages to invoke archiveAccountTasksAction')

    def parse_action_parameters(self):
        self._age_days = self.action_parameters.get('days', 187)
        if (self._age_days is not None):
            self._age_days = int(self.process_label_substitutions(self._age_days))
