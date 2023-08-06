# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import io, yaml, json
from datetime           import datetime
# Core
from coils.core         import *
from coils.net          import *
# DAV Classses
from workflow                          import WorkflowPresentation

class ScheduleObject(DAVObject, WorkflowPresentation):
    ''' Represents a workflow message in a process with a DAV hierarchy. '''

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        self.entry = params['entry']
        
        def _encode(o):
            if isinstance( o, datetime ):
                return  o.strftime( '%Y-%m-%dT%H:%M:%S' )
            raise TypeError( )
        
        self.payload = json.dumps( self.entry, default=_encode )

    def get_property_webdav_getetag(self):
        return self.entry['UUID']

    def get_property_webdav_displayname(self):
        return self.entry['UUID']

    def get_property_webdav_getcontentlength(self):
        #if (self._get_representation()):
        #    return str(len(self.data))
        return len(self.payload)

    def get_property_webdav_getcontenttype(self):
        return 'application/json'

    def get_property_webdav_creationdate(self):
        return datetime.now()

    def do_HEAD(self):
        self.request.simple_response(201,
                             mimetype = 'application/json',
                             headers  = { 'Content-Length':                 self.get_property_webdav_getcontentlength(),
                                          'ETag':                           self.get_property_webdav_getetag() } )

    def do_GET(self):
        self.request.simple_response(200,
                                     data=self.payload,
                                     mimetype='application/json',
                                     headers={
                                         'ETag':                           self.get_property_webdav_getetag()
                                     } )
