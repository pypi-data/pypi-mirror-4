#
# Copyright (c) 2011, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import sys # We use .stdin, .stdout, .stderr, and .exit from sys
import os # We use .getpid from "os".  Generally using "os" is considered BAD
import traceback, logging
from threading        import Thread
from multiprocessing  import Queue
from packet           import Packet
from broker           import Broker
from coils.foundation import ServerDefaultsManager
from service          import Service

AMQ_RECEIVED    = 0
AMQ_TRANSMIT    = 1
AMQ_ACKNOWLEDGE = 2
AMQ_FAIL        = 3
AMQ_TIMEOUT     = 4


class ThreadedService(Service):
    '''
    ThreadedService extends Service but uses a dictionary of threads, one thread
    listens on the AMQ connection - threads can feed the thread-safe queue to create
    a simple main-loop.  ThreadedService can thus receive messages, as well as listen
    for other events (in custom threads), and still provide a simple syncronous main-
    loop.
    '''
    __auto_dispatch__  = False
    __is_worker__      = False
    __TimeOut__        = 10
    threads            = { }   # Dictionary of worker threads maintained by the service

    def __init__(self):
        Service.__init__( self )
        self._event_queue      = Queue( maxsize=4096 )
        self.threads[ 'amqRx'] = Thread( target=self.listen_to_bus, name='amqReceiver', args=( self, ) )

    #
    # Properties
    #

    @property
    def event_queue(self):
        return self._event_queue

    @property
    def is_shutdown(self):
        return not self.RUNNING

    #
    # Setup / Prepare
    #

    def setup(self, silent=True):
        '''
        Perform service setup and start all the registered threads.
        '''
        Service.setup( self, silent=silent )

    def prepare(self):
        '''
        Perform post setup Service preperation for run-loop
        '''
        Service.prepare( self )
        for name, thread in self.threads.items():
            self.log.info( 'Starting thread "{0}"'.format( name ) )
            thread.start( )
            thread.join( 0.1 )
            self.log.info( 'Thread "{0}" started'.format( name ) )

    #
    # Component Plumbing
    #

    def shutdown(self):
        '''
        Change the running state to False, wait for all the threads to terminate, then shutdown
        the Broker and exit.
        '''
        self.RUNNING = False
        self.log.info('Service "{0}" (PID#{1}) shutting down.'.format(self.__service__, os.getpid()))

        for name, thread in self.threads.items( ):
            self.log.info( 'Waiting for the {0} thread to terminate'.format( name ) )
            thread.join()
            self.log.info( '{0} thread has terminated'.format( name ) )

        if self.amq_debug: self.log.debug('Shutting down AMQ broker.')
        self._broker.close()
        if self.amq_debug: self.log.debug('AMQ broker is shutdown.')
        sys.exit(0)

    def listen_to_bus(self, service):
        '''
        Thread method, this listens to the AMQ bus and puts received messages on the event queue
        '''
        if self.amq_debug: self.log.debug( 'Spinning up AMQ bus listener' )
        while self.RUNNING:
            if self._broker.wait( timeout=self.__TimeOut__ ):
                if self.amq_debug: self.log.debug( 'AMQ Bus Timeout' )
                self.event_queue.put( ( AMQ_TIMEOUT, ) )
        if self.amq_debug: self.log.debug( 'AMQ bus listener shutdown' )
        return

    def receive_message(self, message):
        '''
        Called as a handler by the Broker when an AMQ message is recieved.  Attempts to decode
        the message into a Packet and place it on the queue for processing.
        '''
        packet = self._broker.packet_from_message( message )
        if packet:
            if self.amq_debug:
                self.log.debug( 'received "{0}" from "{1}"'.format( packet.uuid, packet.source ) )
            self.event_queue.put( ( AMQ_RECEIVED, packet ))

    def process_packet(self, packet):
        '''
        Called by process_event to deal with an AMQ packet.
        '''
        try:
            method    = Packet.Method(packet.target).lower()
            parameter = Packet.Parameter(packet.target)
        except Exception, e:
            self.log.error('Error decoding packet target: {0}'.format(packet.target))
            self.log.exception(e)
            return False
        else:
            response = self.process_message(method, parameter, packet)
            if (response is not None):
                self.send(response)
            return True

    def process_message(self, method, parameter, packet):
        '''
        Deal with a message from the AMQ bus, mapped to a do_* handler
        '''
        if (self.amq_debug or self.service_debug):
            self.log.debug('Processing message.')
        method = 'do_{0}'.format(method)
        if (hasattr(self, method)):
            if self.amq_debug or self.service_debug:
                self.log.debug('Invoking method: {0}'.format(method))
            try:
                return getattr(self, method)(parameter, packet)
            except Exception, e:
                self.log.exception(e)
                message = 'Exception in method {0} of component {1}.\n{2}'.format(method, self.__service__, traceback.format_exc())
                self.send_administrative_notice(subject='Message processing xception in component {0}'.format(self.__service__),
                                                message=message,
                                                urgency=8,
                                                category='bus')
                raise e
            else:
                if (self.amq_debug or self.service_debug):
                    self.log.debug('{0} completed without exception'.format(method))
        else:
            self.log.error('Service has no such method as {0}'.format(method))
        return None

    def process_service_specific_event(self, event_class, event_data):
        '''
        Children can override this to process events of their own very special types
        '''
        return

    def process_event(self, event):
        '''
        Deal with an event off the event queue
        '''
        if event[0] == AMQ_RECEIVED:
            self.process_packet( event[1] )
        elif event[0] == AMQ_TIMEOUT:
            self.work( )
        else:
            self.process_service_specific_event( event[0], event[1] )

    def run(self, silent=True):
        '''
        Go into the event processing loop.
        '''

        self.RUNNING = True

        self.setup( silent=silent )
        if self.service_debug: self.log.debug( 'Service setup complete.' )
        self.log.debug( 'Service setup complete.' )
        self.prepare( )
        if self.service_debug: self.log.debug( 'Service prepared for run.' )
        self.log.debug( 'Service prepared for run.' )
        self.log.debug( 'Entering event loop.' )
        while self.RUNNING:
            try:
                event = self.event_queue.get( )
                self.process_event( event )
            except  KeyboardInterrupt:
                self.RUNNING = False
        self.shutdown()

    def work(self):
        pass

    #
    # Core method handlers
    #

    def do___shutdown(self, parameter, packet):
        '''
        Received a message to stop running, reply and switch to shutdown mode.
        '''
        self.send( Packet.Reply( packet, { 'status': 200, 'text': 'OK' } ) )
        self.log.info( 'Received a shutdown request.' )
        self.RUNNING=False
