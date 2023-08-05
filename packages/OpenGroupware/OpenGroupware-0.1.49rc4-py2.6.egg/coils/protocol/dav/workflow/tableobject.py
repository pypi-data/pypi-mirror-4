#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime           import datetime
# Core
from coils.core         import *
from coils.net          import *
# DAV Classses
from coils.net          import *

class TableObject(DAVObject):
    ''' Represents a workflow message in a process with a DAV hierarchy. '''

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        self.log.debug(' TableObject named {0} is entity {1}'.format(name, repr(self.entity)))
        self._yaml = None

    def get_yaml_content(self):
        if (self._yaml is None):
            self._yaml = self.entity.as_yaml()
        return self._yaml

    def get_property_webdav_getetag(self):
        return u'{0}'.format(self.entity.name)

    def get_property_webdav_displayname(self):
        return u'{0}'.format(self.entity.name)

    def get_property_webdav_getcontentlength(self):
        return str(len(self.get_yaml_content()))

    def get_property_webdav_getcontenttype(self):
        return 'text/plain'

    def get_property_webdav_creationdate(self):
       #TODO: Maybe we can actually track the date; update a field in the YAML automatically? 
       return datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def do_HEAD(self):
        self.request.simple_response(201,
                                     mimetype=self.get_property_webdav_getcontenttype(),
                                     headers= { 'Content-Length': self.get_property_webdav_getcontentlength(),
                                                'etag':           self.get_property_webdav_getetag() } )

    def do_GET(self):
        self.request.simple_response(200,
                                     data=self.get_yaml_content(),
                                     mimetype=self.get_property_webdav_getcontenttype(),
                                     headers={ 'ETag': self.get_property_webdav_getetag() } )
