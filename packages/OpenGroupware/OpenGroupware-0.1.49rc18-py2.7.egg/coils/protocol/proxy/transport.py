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
import base64, xmlrpclib, httplib

class Transport(xmlrpclib.Transport):
  user_agent = 'OpenGroupware.org COILS proxy service/1.0'
  realhost = None
  proxy = None
  credentials = ()

  def set_proxy(self, proxy):
     self.proxy = proxy

  def make_connection(self, host):
    if (self.proxy != None):
      self.realhost = host
      h = httplib.HTTP(self.proxy)
      return h
    return xmlrpclib.Transport.make_connection(self, host)

  def send_basic_auth(self, connection):
    auth = base64.encodestring('%s:%s' % self.credentials).strip()
    connection.putheader('Authorization', ('Basic %s' % auth))

  def send_request(self, connection, handler, request_body):
    if (self.proxy != None):
      connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))
    else:
      xmlrpclib.Transport.send_request(self, connection, handler, request_body)
  
  def send_host(self, connection, host):
    xmlrpclib.Transport.send_host(self, connection, host)
    if self.proxy != None:
      connection.putheader('Host', self.realhost)
    if self.credentials != ():
      self.send_basic_auth(connection)
