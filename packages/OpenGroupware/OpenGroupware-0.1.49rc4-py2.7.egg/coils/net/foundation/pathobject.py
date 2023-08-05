#
# Copyright (c) 2009, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import sys
from coils.core import *
from xml.sax.saxutils    import escape

class PathObject(object):

    def __init__(self, parent, **params):
        for key in params:
            setattr(self, key, params.get(key))
        self.parent = parent
        log_name = 'pathobject.%s' % self.get_name()
        self.log = logging.getLogger(log_name)

    def init_context(self):
        if (self.context is None):
            metadata = self.request.get_metadata()
            if ( self.is_public() == True ):
                self.context = AnonymousContext(metadata)
            else:
                self.context = AuthenticatedContext(metadata)
        if (self.context is None):
            raise CoilsException('Unable to marshal context')

    def get_path(self):
        ''' Reconstruct the path used to arrive at this object'''
        path = self.get_name()
        x = self.parent
        while (x is not None):
            path = '%s/%s' % (x.get_name(), path)
            x = x.parent
        return path

    def get_absolute_path(self):
        path = self.get_name()
        x = self.parent
        while (x is not None):
            path = '%s/%s' % (x.get_name(), path)
            x = x.parent
        return 'http://{0}:{1}{2}'.format(self.request.server_name, self.request.server_port, escape(path))

    def names(self):
        pass

    def is_public(self):
        return False
        #return True

    def is_folder(self):
        return True

    def is_object(self):
        return False

    def get_name(self):
        return self.name

    def keys(self):
        return []

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        raise NoSuchPathException('No such object as %s at path' % name)

    def do_GET(self, request):
        raise CoilsException('GET method not implemented on this object')

    def do_POST(self, request):
        raise CoilsException('POST method not implemented on this object')

    def do_TRACE(self, request):
        raise CoilsException('TRACE method not implemented on this object')

    def do_PROPFIND(self):
        print '{0} - {1} does not support PROPFIND'.format(self, self.get_path())
        raise CoilsException('PROPFIND method not implemented on this object')

    def do_POST(self, request):
        raise CoilsException('POST method not implemented on this object')

    def do_REPORT(self, request):
        raise CoilsException('REPORT method not implemented on this object')

    def do_MKCOL(self, request):
        raise CoilsException('MKCOL method not implemented on this object')

    def do_DELETE(self, request):
        raise CoilsException('DELETE method not implemented on this object')

    def do_PUT(self, request):
        raise CoilsException('PUT method not implemented on this object')

    def do_COPY(self, request):
        raise CoilsException('COPY method not implemented on this object')

    #def do_MOVE(self, request):
    #    raise CoilsException('MOVE method not implemented on this object')

    def close(self):
        if (hasattr(self, 'context')):
            self.context.close()