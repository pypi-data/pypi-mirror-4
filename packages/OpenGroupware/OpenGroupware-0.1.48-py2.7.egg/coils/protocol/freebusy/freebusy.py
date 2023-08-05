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
from coils.core  import *
from coils.net import *
from vfbobject import VFBObject

class FreeBusy(PathObject, Protocol):
    __pattern__   = [ 'freebusy', '\.vfb$' ]
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def get_name(self):
        return 'freebusy'

    def is_public(self):
        return True
        
    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):        
        x = VFBObject(self, name, request=self.request,
                                  context=self.context,
                                  parameters=self.parameters)
        return x

    def do_GET(self):
        
        responder = VFBObject(self, self.protocol_name, request=self.request,
                                                        context=self.context,
                                                        parameters=self.parameters)
        responder.do_GET()

    def do_POST(self):
        raise CoilsException('POST operations not support for Free/Busy')
