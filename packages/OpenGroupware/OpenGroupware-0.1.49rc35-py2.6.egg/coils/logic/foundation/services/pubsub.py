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
from coils.foundation import *
from coils.core       import *

class PublishSubscribeService(Service):
    __service__ = 'coils.pubsub'
    __auto_dispatch__ = True
    __is_worker__     = False
    
    def __init__(self):
        self._queues = { '__coils__.event.appointment': [ ],
                         '__coils__.event.contact':     [ ],
                         '__coils__.event.enterprise':  [ ],
                         '__coils__.event.participant': [ ],
                         '__coils__.event.process':     [ ],
                         '__coils__.event.project':     [ ],
                         '__coils__.event.resource':    [ ],
                         '__coils__.event.route':       [ ],
                         '__coils__.event.task':        [ ],
                         '__coils__.event.team':        [ ] }

        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)

    def do_list(self, parameter, packet):
        self.send(Packet.Reply(packet, self._queues.keys()))

    def do_create(self, parameter, packet):
        if (parameter is None):
            self.send(Packet.Reply(packet, '500 No name in request'))
            return
        if (name not in self._queues):
            self._queues.set(name, { 'name': parameter,
                                     'creator': Packet.Service(packet.source),
                                     'created': datetime.datetime.now(),
                                     'security': None,
                                     'subscribers': [],
                                     'persist': False })
            self.send(Packet.Reply(packet, '201 {0}'.format(parameter)))
            return
        self.send(Packet.Reply(packet, '200 {0}'.format(parameter)))

    def do_destroy(self, parameter, packet):
        if (parameter is None):
            self.send(Packet.Reply(packet, '500 No name in request'))
            return
        if (parameter in self._queues):
            self._queues.remove(parameter)
            self.send(Packet.Reply(packet, '200 {0}'.format(parameter)))
            return
        self.send(Packet.Reply(packet, '404 {0}'.format(parameter)))

    def do_subscribe(self, parameter, packet):
        if (parameter is None):
            self.send(Packet.Reply(packet, '500 No name in request'))
            return
        elif (parameter in self._queues):
            if (packet.source in self._queues[name]['subscribers']):
                self.send(Packet.Reply(packet, '200 OK'))
                return
            else:
                self._queues[name]['subscribers'].append(packet.source)
                self.send(Packet.Reply(packet, '201 OK'))
                return
        else:
            self.send(Packet.Reply(packet, '404 {0} not found'.format(name)))
            return

    def do_unsubscribe(self, parameter, packet):
        if (parameter is None):
            self.send(Packet.Reply(packet, '500 No name in request'))
        elif (parameter in self._queues):
            if (packet.source in self._queues[name]['subscribers']):
                self._queues[name]['subscribers'].remove(packet.source)
            self.send(Packet.Reply(packet, '200 OK'))
            return
        else:
            self.send(Packet.Reply(packet, '404 {0} not found'.format(name)))
            return

    def do_publish(self, parameter, packet):
        #TODO: This is borked
        return
        if (parameter in self._queues):
            subscribers = self._queues[name]['subscribers']
            for subscriber in subscribers:
                self.send(Packet('{0}/{1}'.format(self.__service__, parameter),
                                                  subscriber,
                                                  packet.data))
        self.send(Packet.Reply(packet, '200 Published'))

