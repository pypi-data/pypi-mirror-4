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
# THE SOFTWARE.
#
import yaml, logging, os
from  coils.foundation.api.amq.transport import Timeout as AMQTimeOut
import coils.foundation.api.amq as amqp
from coils.foundation       import Backend, ServerDefaultsManager
from packet                 import Packet
from exception              import CoilsException, NotImplementedException

EXCHANGE_NAME = 'OpenGroupware_Coils'
EXCHANGE_TYPE = 'direct'

class Broker(object):
    __slots__ = ('_log', '_connection', '_channel', '_tag', '_callbacks', '_subscriptions')
    __AMQDebugOn__     = None
    __AMQConfig__      = None

    def __init__(self):
        sd = ServerDefaultsManager()
        self._log = logging.getLogger('coils.broker[{0}]'.format(os.getpid()))
        if (Broker.__AMQDebugOn__ is None) or (Broker.__AMQConfig__ is None):
            Broker.__AMQDebugOn__ = sd.bool_for_default('BusDebugEnabled')
            Broker.__AMQConfig__  = sd.default_as_dict('AMQConfigDictionary')
        self._callbacks     = { }
        self._subscriptions = { }
        self._connect()
        self._log.info( 'Bus Debug Enabled: {0}'.format( Broker.__AMQDebugOn__) )

    def _connect(self):
        self._connection = amqp.Connection(host='{0}:{1}'.format(Broker.__AMQConfig__.get('hostname', '127.0.0.1'),
                                                                 Broker.__AMQConfig__.get('port', 5672)),
                                           userid       = Broker.__AMQConfig__.get('username', 'guest'),
                                           password     = Broker.__AMQConfig__.get('password', 'guest'),
                                           ssl          = False,
                                           virtual_host = Broker.__AMQConfig__.get('vhost', '/'))
        self._channel = self._connection.channel()
        if (self.debug):
            self._log.debug('connected')
        # This may be a re-connection; so re-subscribe to all the channels that for some reason
        # we believe we should be subscribed to
        for name, data in self.subscriptions.iteritems():
            # data[0] contains the reference to the callback
            # data[1] contains is the queue is durable
            # data[2] contains is auto_delete is enabled
            # data[3] contains exclusive status of the queue
            # data[4] contains the arguments dictionary used to declare the queue
            #  - currently what is in the arguments is mostly just an x-expires value
            self.subscribe(name, data[0], durable=data[1], auto_delete=data[2], exclusive=data[3], arguements=data[4])

    @staticmethod
    def Create():
        return Broker()

    @property
    def subscriptions(self):
        return self._subscriptions

    @property
    def debug(self):
        return Broker.__AMQDebugOn__

    def subscribe(self, name, callback, durable=False,
                                        auto_delete=False,
                                        exclusive=False,
                                        arguements={},
                                        expiration=None):
        routing_key = name.lower()
        # type (Exchange): "fanout", "direct", "topic"
        # durable:  The queue will be recreated with RabbitMQ restarts
        # auto_delete: The queue will be deleted when the last client disconnects
        self._channel.exchange_declare( exchange    = EXCHANGE_NAME,
                                        type        = EXCHANGE_TYPE,
                                        durable     = True,
                                        auto_delete = False )
        # exclusive: only the consumer that creates the queue will be allowed to attach
        if expiration:
            expiration = int(expiration)
            if self.debug:
                self._log.debug('Queue {0} will be created to expire after {1}ms of inactivity.'.format(name, expiration))
            arguements['x-expires'] = expiration
        self._channel.queue_declare(queue       = name ,
                                    durable     = durable,
                                    exclusive   = exclusive,
                                    auto_delete = auto_delete,
                                    arguments  = arguements )
        # any messages arriving at the EXCHANGE_NAME exchange with the specified
        # routing key will be placed in the named queue
        self._channel.queue_bind(queue = name,
                                 exchange = EXCHANGE_NAME,
                                 routing_key = routing_key )
        if not callback:
            callback = self.receive_message
        self._tag = self._channel.basic_consume(queue = name,
                                                no_ack = False,
                                                callback = callback )
        if self.debug:
            self._log.debug('subscribed to {0}'.format(routing_key))
        self._subscriptions[routing_key] = (callback, durable, auto_delete, exclusive, arguements)
        #print 'subscribed to {0}'.format(routing_key)

    def unsubscribe(self, name):
        #TODO: Implement
        raise NotImplementedException('Not Implemented; patches welcome.')

    @property
    def default_source(self):
        if (len(self._subscriptions) > 0):
            default_source = self.subscriptions.keys()[0]
            if (self.debug):
                self._log.debug('defaulting packet source to {0}'.format(default_source))
            return default_source
        else:
            return 'null'

    def send(self, packet, callback=None):
        if (packet.source is None):
            packet.source = '{0}/__null'.format(self.default_source)
        if (self.debug):
            self._log.debug('sending packet {0} with source of {1} to {2}'.format(packet.uuid, packet.source, packet.target))
        message = amqp.Message(yaml.dump(packet))
        message.properties["delivery_mode"] = 2
        routing_key = Packet.Service(packet.target).lower()
        self._channel.basic_publish(message,
                                    exchange = EXCHANGE_NAME,
                                    routing_key = routing_key)
        if (callback is not None):
            if (self.debug):
                self._log.debug('enqueued callback {0}'.format(packet.reply_to))
            self._callbacks[packet.uuid] = callback

    def packet_from_message(self, message):
        packet = yaml.load(message.body)
        if (self.debug):
            self._log.debug('Sending AMQ acknowledgement of message {0}'.format(message.delivery_tag))
        if (packet.source is None):
            raise CoilsException('Broker received a packet with no source address')
        if (packet.target is None):
            raise CoilsException('Broker received a packet with no target address')
        self._channel.basic_ack(message.delivery_tag)
        if (packet.reply_to in self._callbacks):
            if (self._callbacks[packet.reply_to](packet.reply_to, packet.source, packet.target, packet.data)):
                del self._callbacks[packet.reply_to]
                if (self.debug):
                    self._log.debug('dequeued callback {0}'.format(packet.reply_to))
            return None
        return packet

    def receive_message(self, message):
        return self.packet_from_message(message)

    def close(self):
        try:
            self._channel.close()
            self._connection.close()
        except Exception, e:
            self._log.warn('Exception occurred in closing AMQ connection.')
            self._log.exception(e)

    def wait(self, timeout=None):
        if not timeout:
            timeout = 1
        try:
            self._channel.wait(timeout=timeout)
        except AMQTimeOut:
            return None
        except Exception, e:
            self._log.warn('Exception occurred in Broker.wait()')
            self._log.exception(e)
            raise e
