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
import io, yaml, pickle
from datetime           import datetime
# Core
from coils.core         import *
from coils.net          import *
# DAV Classses
from utility            import compile_bpml, \
                                filename_for_route_markup, \
                                filename_for_process_code

class YAMLObject(DAVObject):
    ''' Represent a BPML markup object in WebDAV '''

    def __init__(self, parent, name, **params):
        self.version = None
        DAVObject.__init__(self, parent, name, **params)
        self._payload = None
        if (self.version is None):
            self.version = self.entity.version

    def get_markup(self):
        if (self._payload is None):
            cpm = None
            if (isinstance(self.entity, Route)):
                code = BLOBManager.Open(filename_for_route_markup(self.entity, self.version), 'rb', encoding='binary')
                description, cpm = compile_bpml(code, log=self.log)
                BLOBManager.Close(code)
            elif (isinstance(self.entity, Process)):
                code = BLOBManager.Open(filename_for_process_code(self.entity, self.version), 'rb', encoding='binary')
                cpm = pickle.load(code)
                BLOBManager.Close(code)
            self._payload = yaml.dump(cpm)
        return self._payload

    def get_property_webdav_getetag(self):
        return '{0}:{1}:YAML'.format(self.entity.object_id, self.entity.version)

    def get_property_webdav_displayname(self):
        return self.name

    def get_property_webdav_getcontentlength(self):
        return str(len(self.get_markup()))

    def get_property_webdav_getcontenttype(self):
        return 'application/yaml'

    def get_property_webdav_creationdate(self):
        return datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def do_GET(self):
        ''' Handle a GET request. '''
        self.request.simple_response(200,
                                     data=self.get_markup(),
                                     mimetype='application/yaml',
                                     headers={ 'ETag': self.get_property_webdav_getetag() } )
