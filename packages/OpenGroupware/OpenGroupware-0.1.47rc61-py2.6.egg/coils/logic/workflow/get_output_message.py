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
from coils.core.logic   import GetCommand

class GetOutputMessage(Command):
    __domain__ = "process"
    __operation__ = "get-output-message"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        # TODO: Support using PID
        self.process = params.get('process', None)

    def run(self, **params):
        # TODO: Verify process is completed
        # TODO: Implement security check
        if (self.process is not None):
            self._result = self._ctx.run_command('message::get', uuid=self.process.output_message)
        else:
            self._result = None
