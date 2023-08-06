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
from coils.core     import *

class Publish(Command):
    __domain__    = "service"
    __operation__ = "publish"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        self._source = params.get('source', 'NULL')
        self._target = params.get('target', None)
        self._data = params.get('data', None)

    def run(self, **params):
        self._result = False
        if (self._target is None):
            raise CoilsException('Publish command missing target')
        if (self._ctx.amq_available):
            self._ctx.send(self._source,
                           'coils.pubsub/publish:{0}'.format(self._target),
                           self._data)
            self._result = True
        else:
            self.log.warn('Non-service context, cannot send messages')