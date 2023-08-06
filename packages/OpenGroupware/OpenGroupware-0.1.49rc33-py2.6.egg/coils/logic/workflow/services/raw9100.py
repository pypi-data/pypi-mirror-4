#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import asyncore, threading, socket, Queue, re, urlparse
from coils.core  import *

class ConnectionHandler(asyncore.dispatcher):

    def __init__(self, socket, queue, log, address, size):
        asyncore.dispatcher.__init__(self, sock=socket)
        self.stream = BLOBManager.ScratchFile()
        self.queue = queue
        self.logger = log
        self.available = size
        self.queue_toggle = True
        self.address = address
        if self.logger:
            self.logger.debug('Maximum connection transfer is {0}b'.format(self.available))

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.stream.write(data)
            self.available += (len(data) * -1)
            #if self.log and self.address:
            #    self.log.debug('Read {0}b from {1}; {2}b still available'.format(len(data), self.address, self.available))
            if self.available < 0:
                self.queue_toggle = False
                if self.logger and self.address:
                    self.logger.debug('Closing connection from {0}; stream exceeded maximum size'.format(self.address))
                self.close()

    def handle_close(self):
        self.close()
        if self.queue_toggle:
            self.stream.seek(0)
            self.queue.put((self.address[0], self.stream))
            if self.logger and self.address:
                self.logger.debug('Closing connection from {0}'.format(self.address))


class ConnectionServer(asyncore.dispatcher):

    def __init__(self, host, port, queue, log, maxsize):
        self.queue = queue
        self.logger = log
        self.maxsize=maxsize
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def stop(self):
        self.close()
        asyncore.socket_map.clear()
        raise asyncore.ExitNow

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            self.logger.debug('Incoming connection from {0}'.format(addr))
            handler = ConnectionHandler(socket=sock,
                                        queue=self.queue,
                                        log=self.logger,
                                        address=addr,
                                        size=self.maxsize)


class Raw9100Service(Service):
    __service__ = 'coils.workflow.9100'
    __auto_dispatch__ = True
    __is_worker__     = True

    @property
    def queue(self):
        return self._queue

    @property
    def ctx(self):
        return self._ctx

    def prepare(self):
        Service.prepare(self)
        try:
            sd = ServerDefaultsManager()
            RAW_9100_HOST = sd.string_for_default('Coils9100ListenAddress', '127.0.0.1')
            RAW_9100_MAXSIZE = sd.integer_for_default('Coils9100MaxJobSize', 4294967296)
            self.log.info('Listening on network address "{0}"'.format(RAW_9100_HOST))
            self.log.info('Maximum job size is {0}b'.format(RAW_9100_MAXSIZE))
            self._queue = Queue.Queue()
            self._server = ConnectionServer(RAW_9100_HOST, 9100, queue=self.queue,
                                                                 log=self.log,
                                                                 maxsize=RAW_9100_MAXSIZE)
            self._thread = threading.Thread(target=lambda:asyncore.loop())
            self._thread.start()
            self._ctx = NetworkContext(broker=self._broker)
        except Exception, e:
            self.log.warn('Exception in 9100 component prepare')
            self.log.exception(e)
            raise e
        self.log.info('end prepare')

    def shutdown(self):
        # Create a queue event to flush workers
        self.queue.put((None, None))
        # Request the server stop
        self._server.stop()
        Service.shutdown(self)

    def work(self):
        self.log.info('work')
        # TODO: Component check should be a time-based, not iteration based, component
        stream = None
        try:
            client_ip, stream = self._queue.get(True, timeout=15)
        except Queue.Empty:
            pass
        if stream:
            self.log.info('Processing stream from "{0}"'.format(client_ip))
            first_data = stream.read(1024)
            stream.seek(0)
            #TODO: Place this in a try/catch block and generate a good administrative notice?
            route, args = self.pair_stream(stream=stream, first1k=first_data, client_ip=client_ip)
            if route:
                self.process_stream(stream=stream, route=route, args=args)
            BLOBManager.Close(stream)


    def pair_stream(self, stream, first1k, client_ip):

        def parse_preamble(text):
            if not text: return 0, None, None
            if not isinstance(text, basestring): return 0, None, None
            tmp = re.findall('^::{Workflow:[A-z0-9=_\?&%]*}::', text)
            if not tmp: return 0, None, None
            path = tmp[0]
            leng = len(path)
            name = re.findall('(?<=::{Workflow:)[A-z0-9]*', path)[0]
            args = re.findall('(?<=\?)[A-z0-9=%_&]*', path[len(name) + 12 : -3])
            if args:
                args = urlparse.parse_qs(args[0], keep_blank_values=True)
                tmp = { }
                for key, value in args.items():
                    key = 'xattr_{0}'.format(key.lower())
                    value = value[0]
                    if not value:
                        value = 'YES'
                    tmp[key] = value
                args = tmp
            else:
                args = {}
            return leng, name, args

        def save_to_attachment(stream, ctx, client_ip):
            name = '9100Input.{0}.{1}.data'.format(client_ip, self.ctx.get_timestamp())
            return self.ctx.run_command('attachment::new', handle=stream,
                                                           name=name,
                                                           mimetype='application/octet-stream')

        route = None

        offset, name, args = parse_preamble(first1k)

        if name:
            # A route name was specified in the socket data's preamble
            self.log.info('Stream preamble specified route named "{0}".'.format(name))
            route = self.ctx.run_command('route::get', name=name)
            if not route:
                attachment = save_to_attachment(stream, self.ctx, client_ip)
                self.ctx.commit()
                message = 'Unable to find route "{0}" specified in socket data preamble.\n' \
                          'Possible incorrect permissions or route has been renamed or deleted?\n' \
                          'This stream is being discarded [not processed].\n' \
                          'Client Network Address: {1}\n' \
                          'Content saved in attachment (UUID#{2})\n'.format(name, client_ip, attachment.uuid)
                self.send_administrative_notice(subject='Marshalling Route Named In Preamble Failed',
                                                message=message,
                                                urgency=8,
                                                category='workflow')
            else:
                # We did find a matching route, so we want to move the stream past the preamble
                self.log.info('Paired stream to route "{0}" via preamble.'.format(route.name))
                self.log.debug('Found a stream preamble of {0} bytes, advancing past preamble'.format(offset))
                stream.seek(offset)

        else:
            # Attempt to match stream to a route using the client's network Address
            routes = [ ]

            criteria1 = [ { 'key': 'property.{http://www.opengroupware.us/oie}clientNetworkAddress',
                           'value': client_ip,
                           'conjunction': 'OR',
                           'expression': 'EQUALS' }, ]

            criteria2 = [ { 'key': 'property.{http://www.opengroupware.us/oie}alternateClientNetworkAddress',
                           'value': client_ip,
                           'conjunction': 'OR',
                           'expression': 'EQUALS' } ]

            for criteria in [ criteria1, criteria2, ]:
                tmp = self.ctx.run_command('route::search', criteria=criteria)
                if tmp:
                    routes.extend(tmp)
                    break

            if len(routes) == 0:
                # FAIL: No Candidates
                self.log.info('No matching route found for inbound 9100 connection')
                attachment = save_to_attachment(stream, self.ctx, client_ip)
                self.ctx.commit()
                message = 'No candidate routes found for inbound 9100 connection.\n' \
                          'This message is being discarded.\n' \
                          'Client Network Address: {0}\n' \
                          'Content saved in attachment (UUID#{1})\n'.format(client_ip, attachment.uuid)
                self.send_administrative_notice(subject='9100 Component Input / Route Pairing Failure',
                                    message=message,
                                    urgency=7,
                                    category='workflow',
                                    attachments=[stream])
            elif len(routes) > 1:
                # FAIL: Too many candidates
                self.log.warn('Multiple candidate routes found for inbound 9100 connection; discarding!')
                attachment = save_to_attachment(stream, self.ctx, client_ip)
                self.ctx.commit()
                message = 'Multiple candidate routes found for inbound 9100 connection.\n' \
                          'This message is being discarded.\n' \
                          'Client Network Address: {0}\n' \
                          'Content saved in attachment (UUID#{1})\n'.format(client_ip, attachment.uuid)
                self.send_administrative_notice(subject='9100 Component Input / Route Pairing Failure',
                                                message=message,
                                                urgency=7,
                                                category='workflow')
            elif len(routes) == 1:
                route = routes[0]
                self.log.info('Paired stream from "{0}" to route "{1}" by network address".'.format(client_ip, route.name))

        return route, args

    def process_stream(self, stream, route, args):
        try:
            process = self.ctx.run_command('process::new', values={ 'route_id': route.object_id,
                                                                    'priority': 200},
                                                           mimetype='application/octet-stream',
                                                           rewind=False,
                                                           handle=stream )
            self.log.info('ProcessId#{0} created.'.format(process.object_id))
            if args:
                for key, value in args.items():
                    print key, value
                    self.ctx.property_manager.set_property(process,
                                                           'http://www.opengroupware.us/oie',
                                                           key, value)
            self.ctx.commit()
            self.ctx.run_command('process::start', process=process)
        except Exception, e:
            self.log.warn('failed to create process for 9100 data')
            self.log.exception(e)

