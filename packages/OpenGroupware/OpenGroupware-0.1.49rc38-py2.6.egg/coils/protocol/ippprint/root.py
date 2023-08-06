#
# Copyright (c) 2013
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
import cups
from coils.core        import *
from coils.net         import PathObject, Protocol
from print_queue       import PrintQueue
from printer_list      import PrinterList

class IPPPrint(Protocol, PathObject):
    __pattern__   = [ 'ippprint', ]
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def get_name(self):
        return 'ippprint'

    def is_public(self):
        return False

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        server_name = ServerDefaultsManager().string_for_default( 'DefaultIPPServer', '127.0.0.1' )

        cups.setServer( server_name )
        ipp_connection = cups.Connection( )

        printers = ipp_connection.getPrinters( )

        if name == '.ls':
            return PrinterList(self, name,  request=self.request,
                                            parameters=self.parameters,
                                            context=self.context,
                                            printer_data=printers )
        elif name in printers:
            return PrintQueue(self, name, request=self.request,
                                          parameters=self.parameters,
                                          context=self.context,
                                          ipp_connection=ipp_connection )

        raise NoSuchPathException( 'No such printer as "{0}"'.format( name ) )

    def do_GET(self):
        self.request.simple_response( 200, data='Context is {0}'.format( self.context ) )

    def do_POST(self):
        raise NotImplementedException( 'POST not supported by IPP protocol' )
