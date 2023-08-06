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
from coils.core     import *
from coils.net      import PathObject

class SyncLogin(PathObject):

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def is_public(self):
        return True

    def get_name(self):
        return 'login'

    def do_POST(self):
        print self.get_path()
        payload = self.request.get_request_payload()
        print payload
        import pprint
        pprint.pprint(self)
        response = 'Yo'
        self.request.send_response(200, 'OK')
        self.request.send_header('Content-Length', str(len(response)))
        self.request.send_header('Content-Type', 'text/plain')
        self.request.end_headers()
        self.request.wfile.write(response)
        self.request.wfile.flush()

class SyncLogout(PathObject):

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

class SyncAuth(PathObject):
    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def is_public(self):
        return True

    def get_name(self):
        return 'auth'

    def object_for_key(self, name):
        print self, name
        if (name == 'login'): return SyncLogin(self, request=self.request)
        elif (name == 'logout'): return SyncLogout(self)