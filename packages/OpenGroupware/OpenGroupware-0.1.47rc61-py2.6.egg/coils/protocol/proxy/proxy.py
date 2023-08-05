# Copyright (c) 2010, 2012
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
import xmlrpclib
import transport
import time
from base64 import b64decode
from coils.net import *
from coils.foundation import fix_microsoft_text
from coils.core.omphalos import associate_omphalos_representation, disassociate_omphalos_representation

#transport.set_proxy("squid.mormail.com:3128")
class Proxy(Protocol, PathObject):
    __pattern__   = 'proxy'
    __namespace__ = None
    __xmlrpc__    = False
    __ResultTranscode__ = None

    def __init__(self, parent, **params):
        self.name = 'proxy'
        PathObject.__init__(self, parent, **params)
        if (Proxy.__ResultTranscode__ is None):
            sd = ServerDefaultsManager()
            Service.__PayloadTranscode__ = sd.bool_for_default('CoilsXMLRPCProxyTranscode')
            self.log.debug('XML-RPC Proxy Transcoded Results Enabled')
            Service.__ProxyHost__ = sd.string_for_default('CoilsXMLRPCProxyTarget', value='127.0.0.1')
            self.log.debug('XML-RPC Proxy Target is "{0}"'.format(Service.__ProxyHost__))

    def local_methods(self):
        return [ 'zogi.getLoginAccount', 'zogi.getTombstone' ]

    def do_POST(self):
        request = self.request
        # Set authorization information
        authorization = request.headers.get('authorization')
        if (authorization == None):
            raise AuthenticationException('Authentication Required')
        (kind, data) = authorization.split(' ')
        if (kind == 'Basic'):
            (username, _, password) = b64decode(data).partition(':')
        else:
            raise 'Proxy can only process Basic authentication'
            return

        # Break down request
        payload = request.get_request_payload()

        if (Service.__PayloadTranscode__):
            self.log.debug('XML-RPC Proxy Transcoding Results')
            payload = fix_microsoft_text(payload)
        rpc = xmlrpclib.loads(payload, use_datetime=True)

        # Issue request
        x = transport.Transport()
        x.credentials = (username, password)

        # HACK: If the method is specified to be handled locally then we delegate the work to a
        #       Coils XMLRPCServer object and we leave the Legacy backend out of the loop.
        if rpc[1] in self.local_methods():
            self.log.info('Proxy selecting local method for call to {0}'.format(rpc[1]))
            server = XMLRPCServer(self, self.parent._protocol_dict['RPC2'], context=self.context,
                                                                             request=self.request)
            server.do_POST()
            return
        else:
            # Passing this call to Legacy backend
            self.log.info('Proxy calling remote method for call to {0}'.format(rpc[1]))
            # HACK: Here we pretend that OpenGroupware Legacy understands Coils User Agent descriptions
            #       If a user-agent is known to use associativeLists then we flatten then before sending
            #       the data to the backend server.
            if self.context.user_agent_description[ 'omphalos' ][ 'associativeLists' ]:
                if rpc[1].lower() == 'zogi.putobject':
                    args = disassociate_omphalos_representation( rpc[ 0 ] )
                else:
                    args = rpc[ 0 ]
            else:
                args = rpc[ 0 ]
                
            server = xmlrpclib.Server('http://{0}/zidestore/so/{1}/'.format(Service.__ProxyHost__, username),
                                      transport=x)
        method = getattr(server, rpc[1])

        for attempt in range(1, 3):
            try:
                result = method( *args )
                break
            except xmlrpclib.ProtocolError, err:
                self.log.warn('****Protocol Error, trying again in 0.5 seconds****')
                self.log.exception(err)
                time.sleep(0.5)
            except xmlrpclib.Fault, err:
                # Return the fault to the client; this is BROKEN!
                self.log.warn('Fault code: %d' % err.faultCode)
                self.log.warn('Fault string: %s' % err.faultString)
                return
            except Exception, err:
                self.log.exception(err)
                request.send_response(500, 'XML-RPC Request Failed')
                request.end_headers()
                return

        # HACK: Again we pretend that Legacy can understant Coils User Agent descriptions.
        if self.context.user_agent_description['omphalos']['associativeLists']:
            result = associate_omphalos_representation(result)

        result = xmlrpclib.dumps(tuple([result]), methodresponse=True)

        # HACK: Try to transcode out any unpleasent characters if such feature is enabled.
        if (Service.__PayloadTranscode__):
            self.log.debug('XML-RPC Proxy Transcoding Results')
            result = fix_microsoft_text(result)

        # Send response
        self.request.simple_response(200, data=result, mimetype='text/xml')

        return
