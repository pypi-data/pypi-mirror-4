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
import time
from coils.foundation import *
from coils.core       import *

class ClockService(Service):
    __service__       = 'coils.clock'
    __auto_dispatch__ = True
    __is_worker__     = True
    
    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        self._subscribers = [ ]
        self._alarms      = { }
        self._ctx = AnonymousContext()
        self._ticktock = time.time()
        Service.prepare(self)

    @property
    def ticktock(self):
        if ((time.time() - self._ticktock) > 59):
            self._ticktock = time.time()
            return True
        return False

    @property
    def subscribers(self):
        return self._subscribers

    @property
    def stamp(self):
        x = self._ctx.get_utctime()
        return '{0} {1}'.format(x.strftime('%Y %m %d %H %M %w %a %b'),
                                 int(time.mktime(x.timetuple())))

    def do_subscribe(self, parameter, packet):
        # NOTE: Components that subscribe to the clock will receive a timestamp reply to the
        #       original source of the subscription packet *roughly* event sixty seconds.
        if (packet.source not in self.subscribers):
            self.subscribers.append(packet.source)
        self.send(Packet.Reply(packet, self.stamp))

    def do_unsubscribe(self, parameter, packet):
        if (packet.source in self.subscribers):
            self.subscribers.remove(packet.source)
        self.send(Packet.Reply(packet, self.stamp))

    def do_setalarm(self, parameter, packet):
        try:
            # "t" is the parameter of the target address of the Packet
            # this is expected to be an integer time stamp
            # TODO: document how this relates to timezone; we should be using UTC for alarms
            # From the python docs, time.time() returns:
            # "the time as a floating point number expressed in seconds since the epoch, in UTC"
            # NOTE: Alarms fire once!  They are for a single instance / event.
            source = packet.data.get('alarmTarget', None)
            if (source is None):
                source = packet.source
            t = float(parameter)
            if (t not in self._alarms):
                self._alarms[t] = [ ]
            self._alarms[t].append(source)
        except Exception, e:
            # TODO: Provide better (more meaningul) error response
            self.log.exception(e)
            self.send(Packet.Reply(packet, { 'status': 500, 'test': 'Error'} ) )
        else:
            self.send(Packet.Reply(packet, { 'status': 201, 'test': 'OK'} ) )

    def work(self):
        if (self.ticktock):
            try:
                t = time.time()
                x = self.stamp
                for target in self.subscribers:
                    self.send(Packet('coils.clock/__null', target, x))
                for alarm in self._alarms.keys():
                    if (alarm < t):
                        self.log.debug('firing alarms for {0}'.format(alarm))
                        for target in self._alarms[alarm]:
                            self.log.debug('Sending alarm packet for {0} to {1}'.format(alarm, target))
                            self.send(Packet('coils.clock/__null', target, None))
                    self.log.debug('expiring alarms for {0}'.format(alarm))
                    del self._alarms[alarm]
            except Exception, e:
                # TODO: Provide better (more meaningul) error response
                self.log.exception(e)

