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
from coils.core         import *

class SetAlarm(Command):
    __domain__    = "clock"
    __operation__ = "set-alarm"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._time      = params.get('time', None)
        self._target    = params.get('target', None)
        self._source    = params.get('source', None)
        self._callback  = params.get('callback', None)
        if (self._target is None):
            self._target = self._source
        if (self._time is None):
            raise CoilsException('No time specified for alarm.')

    def run(self):
        self._result = self._ctx.send(self._source,
                                      'coils.clock/setalarm:{0}'.format(self._time),
                                      { 'alarmTarget': self._target },
                                      callback=self._callback)