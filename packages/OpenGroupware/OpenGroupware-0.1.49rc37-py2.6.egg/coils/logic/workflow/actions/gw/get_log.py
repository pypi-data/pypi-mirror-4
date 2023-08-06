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
class GetEntityLogAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "get-entity-log"
    __aliases__   = [ 'getEntityLogAction', 'getEntityLog' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        entries = self._ctx.run_command('object::get-logs', id=self._id)
        for entry in entries:
            self.wfile.write('{0} {1} {2} {3}\r\n'.\
                        format(entry.object_id,
                               entry.datetime.strftime("%Y-%m-%d %H:%M:%S UTC"),
                               entry.action,
                               entry.actor_id))
            self.wfile.write('{0}\r\n'.format(entry.message))
            self.wfile.write('\r\n')

    @property
    def result_mimetype(self):
        return 'text/plain'

    def parse_action_parameters(self):
        self._id = int(self.action_parameters.get('objectId', self.pid))
        #TODO: Support label substitutions - the value must be text
        #self._id = self.process_label_substitutions(self._id)

    def do_epilogue(self):
        pass
