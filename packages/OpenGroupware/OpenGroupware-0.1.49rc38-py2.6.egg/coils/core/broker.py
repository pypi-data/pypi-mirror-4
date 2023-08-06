#
# Copyright (c) 2010, 2013
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
# THE SOFTWARE.
#
import yaml, logging, os, socket, threading
from  coils.foundation.api.amq.transport import Timeout as AMQTimeOut
import coils.foundation.api.amq as amqp
from coils.foundation       import Backend, ServerDefaultsManager
from packet                 import Packet
from exception              import CoilsException, NotImplementedException, CoilsBusException

EXCHANGE_NAME = 'OpenGroupware_Coils'
EXCHANGE_TYPE = 'direct'

class Broker(object):
    __slots__ = ( '_rx_connection', '_rx_channel', '_recv_lock',
                  '_tx_connection', '_tx_channel', '_send_lock',
                  '_log',  '_tag', '_callbacks', '_subscriptions',  )
    __AMQDebugOn__     = None
    __AMQConfig__      = None

    def __init__(self):
        sd = ServerDefaultsManager()
        self._log = logging.getLogger( 'coils.broker[{0}]'.format( os.getpid( ) ) )
        if (Broker.__AMQDebugOn__ is None) or (Broker.__AMQConfig__ is None):
            Broker.__AMQDebugOn__ = sd.bool_for_default('BusDebugEnabled')
            Broker.__AMQConfig__  = sd.default_as_dict('AMQConfigDictionary')
        self._callbacks     = { }
        self._subscriptions = { }
        self._connect()
        self._log.info( 'Bus Debug Enabled: {0}'.format( Broker.__AMQDebugOn__) )
        self._send_lock = threading.Lock( )
        self._recv_lock = threading.Lock( )

    def _connect(self):
        '''
        Connect to the AMQ message service as configured in the server's defaults.
        '''
        amq_username = Broker.__AMQConfig__.get( 'username', 'guest' )
        amq_hostname = Broker.__AMQConfig__.get( 'hostname', '127.0.0.1' )
        amq_hostport = Broker.__AMQConfig__.get( 'port', '5672' )
        amq_password = Broker.__AMQConfig__.get( 'password', 'guest' )
        amq_virtname = Broker.__AMQConfig__.get( 'vhost', '/' )

        amq_url = 'amqp://{0}@{1}:{2}/{3}"'.format( amq_username,
                                                    amq_hostname,
                                                    amq_hostport,
                                                    amq_virtname )
        self._log.info( 'Binding to message broker @ "{0}"'.format( amq_url ) )

        try:
            # Receive channel
            self._rx_connection = amqp.Connection( host     ='{0}:{1}'.format( amq_hostname, amq_hostport ),
                                                   userid   = amq_username,
                                                   password = amq_password,
                                                   ssl      = False,
                                                   virtual_host = amq_virtname )
            self._rx_channel = self._rx_connection.channel( )

            # Transmit channel
            self._tx_connection = amqp.Connection( host         = '{0}:{1}'.format( amq_hostname, amq_hostport ),
                                                   userid       = amq_username,
                                                   password     = amq_password,
                                                   ssl          = False,
                                                   virtual_host = amq_virtname )
            self._tx_channel = self._tx_connection.channel( )

        except socket.error, e:
            message = 'Unable to bind to message broker "{0}"'.format( amq_url )
            self._log.exception(e)
            raise CoilsBusException( message )

        if self.debug:
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
            self.subscribe( name, data[0], durable=data[1], auto_delete=data[2], exclusive=data[3], arguements=data[4] )

    @staticmethod
    def Create():
        '''
        Factory method to create a Broker object
        '''
        return Broker()

    @property
    def subscriptions(self):
        '''
        Retrieve a reference to the current list of subscriptions
        '''
        return self._subscriptions

    @property
    def debug(self):
        return Broker.__AMQDebugOn__

    def subscribe(self, name, callback, durable=False,
                                        auto_delete=False,
                                        exclusive=False,
                                        arguements={},
                                        expiration=None,
                                        queue_type='direct',
                                        consume=True,
                                        exchange_name='OpenGroupware_Coils'):
        '''
        Create and bind to the specified message queue.

        :param name:
        :param callback:
        :param durable:  The queue will be recreated with RabbitMQ restarts
        :param auto_delete:  The queue will be deleted when the last client disconnects
        :param exclusive:
        :param arguements:
        :param expiration: only the consumer that creates the queue will be allowed to attach
        :param queue_type: The type of exchange queue to create - fanout, direct, or topic
        :param consume: Recieve messages on the created exchange
        '''

        routing_key = name.lower()

        if queue_type not in ('fanout', 'direct', 'topic'):
            raise CoilsBusException( 'Attempt to create queue of unknown type "{0}"'.format( queue_type ) )

        self._send_lock.acquire( )
        self._recv_lock.acquire( )
        try:
            self._log.info(' AMQ EXCHANGE DECLARE: {0} [type: {1} durable: {2} autodelete: {3}]'.\
                format( EXCHANGE_NAME, queue_type, durable, auto_delete ) )
            self._rx_channel.exchange_declare( exchange    = exchange_name,
                                               type        = queue_type,
                                               durable     = True,
                                               auto_delete = auto_delete )
            if expiration:
                expiration = int( expiration )
                if self.debug:
                    self._log.debug('Queue {0} will be created to expire after {1}ms of inactivity.'.format(name, expiration))
                arguements['x-expires'] = expiration

            self._log.info(' AMQ QUEUE DECLARE: {0} [durable: {1} autodelete: {2} exclusive: {3}]'.\
                format( name, durable, auto_delete, exclusive ) )
            for key, value in arguements.items( ):
                self._log.info('AMQ QUEUE PARAMS: {0}.{1} = "{2}"'.format( name, key, value ) )
            self._rx_channel.queue_declare( queue       = name ,
                                            durable     = durable,
                                            exclusive   = exclusive,
                                            auto_delete = auto_delete,
                                            arguments   = arguements )

            # any messages arriving at the EXCHANGE_NAME exchange with the specified
            # routing key will be placed in the named queue
            if queue_type == 'fanout':
                self._rx_channel.queue_bind( queue = name,
                                             exchange = exchange_name,)
            else:
                self._rx_channel.queue_bind( queue = name,
                                             exchange = exchange_name,
                                             routing_key = routing_key )

            if consume:
                if not callback:
                    callback = self.receive_message

                tag = self._rx_channel.basic_consume( queue = name,
                                                      no_ack = False,
                                                      callback = callback )
                if self.debug:
                    self._log.debug( 'subscribed to "{0}" with tag "{1}"'.format( routing_key, tag ) )

                self._subscriptions[ routing_key ] = ( callback, durable, auto_delete, exclusive, arguements, tag )
            elif self.debug:
                self._log.debug( 'Created queue "{0}" without consumption'.format( routing_key, tag ) )
        finally:
            self._recv_lock.release( )
            self._send_lock.release( )

    def unsubscribe(self, name):
        #TODO: Implement
        raise NotImplementedException( 'Not Implemented; patches welcome.' )

    @property
    def default_source(self):
        if (len(self._subscriptions) > 0):
            default_source = self.subscriptions.keys()[0]
            if (self.debug):
                self._log.debug('defaulting packet source to {0}'.format(default_source))
            return default_source
        else:
            return 'null'

    def send(self, packet, callback=None, exchange='OpenGroupware_Coils', fanout=False):
        if (packet.source is None):
            packet.source = '{0}/__null'.format(self.default_source)
        if self.debug:
            self._log.debug('sending packet {0} with source of {1} to {2}'.format(packet.uuid, packet.source, packet.target))
        message = amqp.Message(yaml.dump(packet))
        message.properties["delivery_mode"] = 2
        routing_key = Packet.Service(packet.target).lower()

        self._send_lock.acquire( )
        try:
            if fanout:
                self._tx_channel.basic_publish( message, exchange = exchange, )
            else:
                self._tx_channel.basic_publish( message,
                                                exchange = exchange,
                                                routing_key = routing_key )
            if callback:
                if self.debug:
                    self._log.debug( 'enqueued callback to {0} for {1}'.format( callback, packet.uuid ) )
                self._callbacks[ packet.uuid ] = callback
        finally:
            self._send_lock.release( )
        return packet.uuid

    def packet_from_message(self, message):
        packet = yaml.load( message.body )
        if self.debug:
            self._log.debug( 'Sending AMQ acknowledgement of message {0}'.format( message.delivery_tag ) )
        if packet.source is None:
            raise CoilsException( 'Broker received a packet with no source address' )
        if packet.target is None:
            raise CoilsException( 'Broker received a packet with no target address' )
        self._rx_channel.basic_ack( message.delivery_tag )
        if ( packet.reply_to in self._callbacks ):
            if ( self._callbacks[ packet.reply_to ]( packet.reply_to, packet.source, packet.target, packet.data )) :
                del self._callbacks[ packet.reply_to ]
                if self.debug:
                    self._log.debug( 'dequeued callback {0}'.format( packet.reply_to ) )
            return None
        return packet

    def receive_message(self, message):
        return self.packet_from_message( message )

    def close(self):
        try:
            self._rx_channel.close()
            self._rx_connection.close()
            self._tx_channel.close()
            self._tx_connection.close()
        except Exception, e:
            self._log.warn('Exception occurred in closing AMQ connection.')
            self._log.exception(e)

    def wait(self, timeout=None):
        with self._recv_lock:
            if not timeout:
                timeout = 1
            try:
                self._rx_channel.wait( timeout=timeout )
            except AMQTimeOut:
                return None
            except Exception, e:
                self._log.warn('Exception occurred in Broker.wait()')
                self._log.exception(e)
                raise e
