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
from coils.core          import *
from coils.foundation    import *
from coils.core.logic    import DeleteCommand
from utility             import *

class DeleteProcess(DeleteCommand):
    __domain__ = "process"
    __operation__ = "delete"

    def get_by_id(self, pid, access_check):
       return self._ctx.run_command('process::get', id=pid, access_check=access_check)

    def run(self):
        self.log.debug('Deleting data for processId#{0}'.format(self.obj.object_id))
        BLOBManager.DeleteShelf(uuid=self.obj.uuid)
        messages = self._ctx.run_command('process::get-messages', process=self.obj)
        for message in messages:
            self.log.debug('Deleting message {0}'.format(message.uuid))
            self._ctx.run_command('message::delete', uuid=message.uuid)
        for vid in range(self.obj.version):
            BLOBManager.Delete(filename_for_versioned_process_code(self.obj.object_id, vid))
        for filename in [ filename_for_process_markup(self.obj),
                           filename_for_process_code(self.obj) ]:
            BLOBManager.Delete(filename)
        DeleteCommand.run(self)
