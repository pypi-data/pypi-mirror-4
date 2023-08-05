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
from datetime import datetime
from StringIO import StringIO
from time import strftime
from davobject import DAVObject
from bufferedwriter import BufferedWriter

class StaticObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_webdav_displayname(self):
        return DAVObject.get_property_webdav_displayname(self)

    def get_property_webdav_getcontentlength(self):
        return unicode(len(self.payload))

    def get_property_webdav_getcontenttype(self):
        return self.mimetype

    def _load_self(self):
        return True

    def do_GET(self):
       self.request.simple_response(200,
                                    data=self.payload,
                                    mimetype=self.get_property_webdav_getcontenttype())