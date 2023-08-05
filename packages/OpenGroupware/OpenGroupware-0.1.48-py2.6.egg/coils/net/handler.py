#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import sys, logging, urllib, urlparse, os
from base64               import b64decode
from BaseHTTPServer       import BaseHTTPRequestHandler
from coils.net.root       import RootFolder
from coils.core           import CoilsException, \
                                  NoSuchPathException, \
                                  AuthenticationException, \
                                  AccessForbiddenException

class CoilsRequestHandler(BaseHTTPRequestHandler):
    # client_address
    # server
    # command
    # path
    # request_version
    # headers (MessageClass of the request headers)
    # rfile - stream of the body of the request
    # wfile - output stream of the response

    def __init__(self, request, client_address, server):
        self.payload = None
        self.log = logging.getLogger('http')
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.protocol_version = 'HTTP/1.1'

    @property
    def protocol_version(self):
        if (self.request_version == 'HTTP/1.0'):
            return 'HTTP/1.0'
        return 'HTTP/1.1'

    @property
    def user_agent_string(self):
        return self.headers.get('USER-AGENT', 'Unknown')

    @property
    def server_name(self):
        return self.server.server_name

    @property
    def server_port(self):
        return self.server.server_port

    def get_request_payload(self):
        if (self.command == 'GET'):
            return None
        if (self.payload is None):
            if 'Content-length' in self.headers:
                self.payload = self.rfile.read(int(self.headers['Content-length']))
            else:
                self.log.warn('Request had not Content-Length header')
                self.payload = ''
                #self.wfile.write("HTTP/1.1 100 Continue\r\n\r\n")
                #self.payload = self.rfile.read()
            #self.log.debug('Request: {0} {1}'.format(self.command, self.payload))
        return self.payload

    def get_metadata(self):
        metadata = { }
        metadata['amq_broker'] = self.server.broker
        metadata['connection'] = { }
        metadata['connection']['user_agent'] = self.user_agent_string
        metadata['connection']['client_address'] = self.client_address[0]
        metadata['connection']['client_port']    = self.client_address[1]
        metadata['authentication'] = { }
        authorization = self.headers.get('authorization')
        if (authorization == None):
            claimstobe = self.headers.get('X-REMOTE-USER')
            if (claimstobe is None):
                metadata['authentication']['mechanism'] = 'anonymous'
            else:
                metadata['authentication']['mechanism'] = 'trust'
                metadata['authentication']['claimstobe'] = claimstobe
        else:
            (kind, data) = authorization.split(' ')
            if (kind.upper() == 'BASIC'):
                (username, _, password) = b64decode(data).partition(':')
                metadata['authentication']['login'] = username
                metadata['authentication']['claimstobe'] = username
                metadata['authentication']['secret'] = password
                metadata['authentication']['options'] = { }
                metadata['authentication']['mechanism'] = 'PLAIN'
            else:
                metadata['authentication']['mechanism'] = 'UNKNOWN'
                raise AuthenticationException(401, 'Only BASIC Authentication Supported')
        metadata['path'] = self.path
        return metadata

    def marshall_handler(self, root, url):
        ''' Retrieve the handler object, a PathObject, to process the request
            This method returns None if there is no handler for the path.
            A path may be, at most, 64 elements long '''
        #path = self.path[1:]
        path       = urllib.unquote(url.path[1:])
        self.log.debug('Request for {0}'.format(urllib.unquote(path)))
        if (path[-1:] == '/'):
            path=path[:-1]
        path_elements = path.split('/', 64)
        if (self.command in [ 'PUT', 'DELETE', 'MOVE', 'MKCOL' ]):
            # If request is a PUT then we drop the last element of the path
            # for handler look-up since a PUT is managed by the collection
            # containing the resource, not the resource itself (which may not
            # exist yet if the PUT is intended to create the resource).
            self.request_name = path_elements[-1:][0]
            path_elements = path_elements[:-1]
        handler = root
        for i in range(len(path_elements)):
            # Any of these objects in the tree may throw an exception,
            # most notably a 401 (Authentication Required) or a 404
            # (No such path).
            if (len(path_elements[i]) > 0):
                handler = handler.object_for_key(urllib.unquote(path_elements[i]))
                if (handler is None):
                    raise NoSuchPathException('No such path as {0}'.format(path_elements[i]))
        self.log.debug('Selected {0} as handler'.format(repr(handler)))
        url           = None
        path          = None
        parameters    = None
        path_elements = None
        return handler

    def process_request(self):
        """Respond to a request"""
        handler = None
        url  = urlparse.urlparse(self.path)
        root = RootFolder(request=self,
                          parameters=urlparse.parse_qs(url.query, True))
        try:

            handler = self.marshall_handler(root, url)
            if (handler is None):
                # Was unable to marshall a handler for the requested path
                raise NoSuchPathException(self.path)
            else:
                
                if (self.command in [ 'PUT', 'DELETE', 'MOVE', 'MKCOL' ] ):
                    # In the case of a PUT the do_ method expects the name of the
                    # request as the last element is the target resource within the
                    # managing collection.
                    getattr(handler, 'do_{0}'.format(self.command))(self.request_name)
                else:
                    getattr(handler, 'do_{0}'.format(self.command))()
                # release handler
        except AuthenticationException, err:
            self.log.exception(err)
            self.simple_response(401,
                                 message='Authentication Required',
                                 mimetype='text/plain',
                                 data='Authentication failure',
                                 headers={'WWW-Authenticate': 'Basic realm="OpenGroupware COILS"' })
        except NoSuchPathException, err:
            self.log.exception(err)
            self.simple_response(404,
                                 message='No such path as {0}'.format(self.path),
                                 mimetype='text/plain',
                                 data='No such path',
                                 headers={ 'WWW-Authenticate': 'Basic realm="OpenGroupware COILS"' })
        except AccessForbiddenException, err:
            self.log.exception(err)
            self.simple_response(err.error_code(),
                                 data=err.error_text(),
                                 mimetype='text/plain',
                                 message='Access forbidden')
            return
        except CoilsException, err:
            self.log.exception(err)
            self.simple_response(err.error_code(),
                                 data=err.error_text(),
                                 mimetype='text/plain',
                                 message='Coils Exception')
        except Exception, err:
            self.log.exception(err)
            self.simple_response(500,
                                 message='Error',
                                 mimetype='text/plain',
                                 data=str(err))
        finally:
            if (root.context is not None):
                root.context.close()
            handler = None
            root = None

    def do_GET(self):
        ''' Respond to a GET request '''
        self.process_request()

    def do_POST(self):
        ''' Respond to a POST request '''
        self.process_request()

    def do_PUT(self):
        ''' Respond to a PUT request '''
        self.process_request()
        
    def do_MKCOL(self):
        ''' Respond to a MKCOL request '''
        self.process_request()

    def do_DELETE(self):
        ''' Respond to a DELETE request '''
        self.process_request()

    def do_OPTIONS(self):
        ''' Respond to a OPTIONS request '''
        self.process_request()

    def do_PROPFIND(self):
        ''' Respond to a PROPFIND request '''
        self.process_request()

    def do_PROPPATCH(self):
        ''' Respond to a PROPPATCH request '''
        self.process_request()

    def do_REPORT(self):
        ''' Respond to a REPORT request '''
        self.process_request()

    def do_HEAD(self):
        ''' Respond to a HEAD request '''
        self.process_request()

    def do_LOCK(self):
        ''' Respond to a LOCK request '''
        self.process_request()

    def do_UNLOCK(self):
        ''' Respond to a UNLOCK request '''
        self.process_request()

    def do_MOVE(self):
        ''' Respond to a MOVE request '''
        self.process_request()

    def send_headers(self, headers):
        for header in headers:
            self.send_header(header, headers.get(header))

    #
    # Plumbing
    #

    def _status_message(self, status, message=None):
        if (message is None):
            if (status == 200): message = 'OK'
            elif (status == 201): message = 'Created'
            elif (status == 204): message = 'Updated'
            elif (status == 207): message = 'Multistatus'
            elif (status == 301): message = 'Moved'
            else: message = '??????'
        return message

    def _send_headers(self, headers):
        for header in headers:
            self.send_header(header, headers.get(header))

    def simple_response(self, status,
                              data=None,
                              stream=None,
                              mimetype='application/octet-stream',
                              headers={},
                              message=None):
        ''' Sends an HTTP/1.0 style response with a Content-Length header '''
        # TODO: Be aware of client request protocol version
        message = self._status_message(status, message=message)
        self.send_response(status, message)
        # Find and produce a Content-Length header
        if ('Content-Length' not in headers):
            if (data is None):
                if (stream is None):
                    size = 0
                else:
                    stream.seek(0, os.SEEK_END)
                    size = stream.tell()
            else:
                if (isinstance(data, int)): data = unicode(data)
                size = len(data)
            self.send_header('Content-Length', unicode(size))
        # Send Content-Type header
        if (('Content-Type' not in headers) and (mimetype is not None)):
            self.send_header('Content-Type', mimetype)
        # Send custom headers
        self.send_headers(headers)
        # Request the client drop the connection after the response
        # TODO: Can we support pipelining?
        if self.protocol_version == 'HTTP/1.1':
            self.send_header('Connection', 'close')
        self.end_headers()
        # Send Data
        if (data is not None):
            self.wfile.write(data)
        elif (stream is not None):
            c = True
            stream.seek(0)
            while c:
                data = stream.read(65535)
                if (len(data) > 0):
                    self.wfile.write(data)
                else:
                    c = False
        self.wfile.flush()

    def stream_response(self, status,
                              stream=None,
                              mimetype='application/octet-stream',
                              headers={},
                              message=None,
                              fallback=True):
        if self.request_version == 'HTTP/1.0':
            if (fallback):
                self.simple_response(status, stream=stream, mimetype=mimetype, headers=headers, message=message)
            else:
                raise CoilsException('HTTP/1.0 cannot support data streams, use an HTTP/1.1 client.')
        else:
            message = self._status_message(status, message=message)
            self.send_response(status, message)
            if ('Content-Type' not in headers):
                self.send_header('Content-Type', mimetype)
            self.send_header('Transfer-Encoding', 'chunked')
            self.send_header('Connection', 'close')
            self._send_headers(headers)
            self.end_headers()
            c = True
            while c:
                data = stream.read(65535)
                if (len(data) > 0):
                    length = len(data)
                    self.wfile.write("%x\r\n" % (len(data)))
                    self.wfile.write(data)
                    self.wfile.write("\r\n")
                else:
                    c = False
            self.wfile.write("0\r\n")
            self.wfile.write("\r\n")
            self.wfile.flush()

    def generator_response(self, status, generator=None,
                                         mimetype='application/octet-stream',
                                         headers={},
                                         message=None,
                                         fallback=True):
        if self.request_version == 'HTTP/1.0':
            if (fallback):
                self.simple_response(status, stream=stream, mimetype=mimetype, headers=headers, message=message)
            else:
                raise CoilsException('HTTP/1.0 cannot support data streams, use an HTTP/1.1 client.')
        else:
            #TODO: Implement
            pass

    def send_start_stream(self, headers, content_type):
        self.send_response(200, 'OK')
        self.send_headers(headers)
        self.send_header('Content-Type', content_type)
        self.send_header('Transfer-Encoding', 'chunked')
        self.send_header('Connection', 'close')
        self.end_headers()

    def send_to_stream(self, data):
        length = len(data)
        self.wfile.write("%x\r\n" % (len(data)))
        self.wfile.write(data)
        self.wfile.write("\r\n")

    def send_end_stream(self):
        self.wfile.write("0\r\n")
        self.wfile.write("\r\n")
        self.wfile.flush()
