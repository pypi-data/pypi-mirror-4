#!/usr/bin/env python
# Copyright (c) 2010, 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
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
import shutil
from tempfile            import mkstemp
from coils.core          import *
from coils.core.logic    import ActionCommand

class QueueProcessAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "queue-process"
    __aliases__   = [ 'queueProcess', 'queueProcessAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def do_action(self):
        input_handle = BLOBManager.ScratchFile(suffix='.message')
        shutil.copyfileobj(self.rfile, input_handle)
        route = self._ctx.run_command('route::get', name=self._route_name)
        if (route is not None):
            process = self._ctx.run_command('process::new', values={ 'route_id': route.object_id,
                                                                     'handle': input_handle } )
            process.state = 'Q'
            process.priority = self._priority
            self.wfile.write(unicode(process.object_id))
        else:
            raise CoilsException('No such route as {0}'.format(self._route_name))
        BLOBManager.Close(input_handle)


    def parse_action_parameters(self):
        self._route_name = self.action_parameters.get('routeName', None)
        self._priority = int(self.action_parameters.get('priority', 100))
        if (self._route_name is None):
            raise CoilsException('No such route to queue process.')

    def do_epilogue(self):
        ActionCommand.do_epilogue(self)
