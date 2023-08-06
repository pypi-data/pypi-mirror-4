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
from StringIO                           import StringIO
from datetime                           import datetime
from coils.core                         import *
from coils.net                          import *
from messageobject                      import MessageObject
from workflow                           import WorkflowPresentation

class LoadScheduleObject(DAVObject):
    ''' Represent a BPML markup object in WebDAV '''
    
    def __init__(self, parent, name, **params):
        self.version = None
        DAVObject.__init__(self, parent, name, **params)
        self.text = None

    def get_property_webdav_getetag(self):
        #TODO: Make this a proper etag, it must change on change
        return 'loadSchedule'

    def get_property_webdav_displayname(self):
        return 'Workflow load schedule'

    def get_property_webdav_getcontentlength(self):
        self.generate_schedule()
        return str(len(self.text))

    def get_property_webdav_getcontenttype(self):
        return 'text/plain'

    def get_property_webdav_creationdate(self):
        return datetime.now()

    def get_property_webdav_getlastmodified(self):
        return datetime.now()

    def generate_schedule(self):
        if self.text is None:
            stream = StringIO(u'')
            for column in ['Hour', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
                stream.write(u' {0} '.format(column))
            stream.write('\r\n')
            for hour in range(24):
                stream.write(u' {0:#2} '.format(hour))
                for day in range(7):
                    stream.write(u' {0:#4} '.format(10))
                stream.write('\r\n')
            self.text = stream.getvalue()
            stream.close()
            stream = None

    def do_GET(self):
        ''' Handle a GET request. '''
        self.generate_schedule()
        self.request.simple_response(200,
                                     data=self.text,
                                     mimetype='application/text',
                                     headers={ 'ETag': self.get_property_webdav_getetag() } )
