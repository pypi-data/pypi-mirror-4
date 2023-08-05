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
from coils.core.logic    import ActionCommand

# TODO: Support retrieval of the log as XML
# TODO: The process::get-log command now supports a syncronous mode, this action
#       should use that rather than containing its own callback cruft.
class GetProcessLogAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "get-process-log"
    __aliases__   = [ 'getProcessLogAction', 'getProcessLog' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        self._flag = False
        log_text = self._ctx.run_command('process::get-log', pid=self._id,
                                                             format=self._format)
        if log_text:
            self.wfile.write(log_text)
        else:
            self.log.warn('No or emtpy response from process logger component')
            self.wfile.write('process log not available')
        # TODO: Should we fail [raise exception] when we don't hear back from the component?

    @property
    def result_mimetype(self):
        return 'text/plain'

    def parse_action_parameters(self):
        self._id     = int(self.action_parameters.get('processId', self.pid))
        self._format = self.action_parameters.get('format', 'text/plain')
        #TODO: Support label substitutions - the value must be text
        #self._id = self.process_label_substitutions(self._id)

    def do_epilogue(self):
        pass
