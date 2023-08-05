# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
import io
from datetime           import datetime
# Core
from coils.core         import *
from coils.net          import *
# DAV Classses
from coils.net          import *
from utility            import filename_for_route_markup, \
                                 filename_for_process_markup

class BPMLObject(DAVObject):
    ''' Represent a BPML markup object in WebDAV '''
    
    def __init__(self, parent, name, **params):
        self.version = None
        DAVObject.__init__(self, parent, name, **params)
        if (self.version is None):
            self.version = self.entity.version

    def get_property_webdav_getetag(self):
        return '{0}:{1}'.format(self.entity.object_id, self.version)

    def get_property_webdav_displayname(self):
        if (isinstance(self.entity, Route)):
            return 'BPML Markup of route {0}'.format(self.entity.name)
        elif (isinstance(self.entity, Process)):
            return 'BPML Markup for process {0}'.format(self.entity.object_id)
        raise CoilsException('Invalid entity for BPMLObject')

    def get_property_webdav_getcontentlength(self):
        markup = self.entity.get_markup()
        if (markup is None):
            return u'0'
        return unicode(len(self.entity.get_markup()))

    def get_property_webdav_getcontenttype(self):
        return 'application/xml'

    def get_property_webdav_creationdate(self):
        # TODO: Return a meaningful value
        # Issue#163: Implement BPMLObject's creation-date
        return datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def do_GET(self):
        ''' Handle a GET request. '''
        if (isinstance(self.entity, Route)):
            handle = BLOBManager.Open(filename_for_route_markup(self.entity, self.version), 'rb', encoding='binary')
        else:
            handle = BLOBManager.Open(filename_for_process_markup(self.entity), 'rb', encoding='binary')
        self.request.stream_response(200,
                                     stream=handle,
                                     mimetype='application/xml',
                                     headers={ 'etag': self.get_property_webdav_getetag() } )
        BLOBManager.Close(handle)
