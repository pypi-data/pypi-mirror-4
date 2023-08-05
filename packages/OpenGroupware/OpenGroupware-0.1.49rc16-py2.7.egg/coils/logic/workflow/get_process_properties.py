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
from sqlalchemy         import *
from coils.core         import *

class GetProcessProperties(Command):
    __domain__ = "process"
    __operation__ = "get-properties"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._obj = params.get('process', params.get('object', None))
        if (self._obj is None):
            self._pid = params.get('pid', params.get('id', None))
        else:
            self._pid = self._obj.object_id
        self._context_id = params.get('runas', self._ctx.account_id)
        self._callback = params.get('callback', None)
        if (self._pid is None):
            raise CoilsException('ProcessId required to retreive process OIE proprties')

    def run(self):
        self._result = self._ctx.send(None,
                                      'coils.workflow.manager/get_properties:{0}'.format(self._pid),
                                      None,
                                      callback = self._callback)
