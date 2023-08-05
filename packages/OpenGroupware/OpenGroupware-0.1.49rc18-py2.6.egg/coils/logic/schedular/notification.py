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
from time             import time
from coils.foundation import *
from coils.core       import *

class NotificationService(Service):
    __service__ = 'coils.schedular.notification'
    __auto_dispatch__ = True
    __is_worker__     = False

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        self._iter = 0
        Service.prepare(self)
        packet = Packet('coils.schedular.notification/ticktock',
                        'coils.clock/subscribe',
                        None)
        self.send(packet)
        self._time = time() + 100
        self._ctx = AdministrativeContext()

    def iteration(self):
        self._iter = self._iter + 1
        return self._iter

    def do_list_notifications(self, route, packet):
        self.send(Packet.Reply(packet, '500 Not implemented'))

    def do_ticktock(self, parameter, packet):
        # TODO: Implement
        # Time format is: 2010 05 03 01 45 1 Mon May 1272869144 (all in GMT)
        pass

