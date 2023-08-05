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
from coils.foundation import *
from coils.core       import *
from coils.core.logic import DeleteCommand

class DeleteAppointment(DeleteCommand):
    __domain__ = "appointment"
    __operation__ = "delete"

    def delete_comment(self):
        self._ctx.run_command('appointment::delete-comment', appointment=self.obj)

    def delete_participants(self):
        self._ctx.run_command('appointment::delete-participants', object=self.obj)

    def run(self):
        if (self.obj is None):
            raise CoilsException('No appointment provided for deletion.')
        self.delete_participants()
        self.delete_comment()
        DeleteCommand.run(self)