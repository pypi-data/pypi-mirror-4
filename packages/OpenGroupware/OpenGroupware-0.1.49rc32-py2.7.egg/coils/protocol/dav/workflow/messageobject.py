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
from coils.net.ossf     import MarshallOSSFChain
from workflow           import WorkflowPresentation

class MessageObject(DAVObject, WorkflowPresentation):
    ''' Represents a workflow message in a process with a DAV hierarchy. '''

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        self.log.debug(' MessageObject named {0} is entity {1}'.format(name, repr(self.entity)))

    def get_property_webdav_getetag(self):
        return '{0}:{1}'.format(self.entity.uuid, self.entity.version)

    def get_property_webdav_displayname(self):
        if (hasattr(self.parent, 'label_type')):
            if (self.parent.label_type == 'label'):
                if (self.entity.label is not None):
                    return self.entity.label
        return self.entity.uuid[1:-1]

    def get_property_webdav_getcontentlength(self):
        #if (self._get_representation()):
        #    return str(len(self.data))
        return str(self.entity.size)

    def get_property_webdav_getcontenttype(self):
        return self.entity.mimetype

    def get_property_webdav_creationdate(self):
        if (self.entity.created is None):
            return datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        else:
            return self.entity.created.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def do_HEAD(self):
        if (self.entity.label is None):
            label = '__undefined__'
        else:
            label = self.entity.label
        self.request.simple_response(201,
                             mimetype = self.entity.mimetype,
                             headers  = { 'Content-Length':                 str(self.entity.size),
                                          'ETag':                           self.get_property_webdav_getetag(),
                                          'X-COILS-WORKFLOW-MESSAGE-UUID':  self.entity.uuid,
                                          'X-COILS-WORKFLOW-PROCESS-ID':    self.process.object_id,
                                          'X-COILS-WORKFLOW-MESSAGE-LABEL': label} )

    def do_GET(self):
        if (self.entity.label is None):
            label = '__undefined__'
        else:
            label = self.entity.label
        handle = self.get_message_handle(self.entity)
        if (handle is None):
            raise CoilsException('Unable to open handle to message content.')
        self.log.debug('Document MIME-Type is "{0}"'.format(self.entity.mimetype))
        handle, mimetype = MarshallOSSFChain(handle, self.entity.mimetype, self.parameters)
        self.log.debug('MIME-Type after OSSF processing is {0}'.format(mimetype))
        self.request.stream_response(200,
                                     stream=handle,
                                     mimetype=mimetype,
                                     headers={
                                         'ETag':                           self.get_property_webdav_getetag(),
                                         'X-COILS-WORKFLOW-MESSAGE-UUID':  self.entity.uuid,
                                         'X-COILS-WORKFLOW-MESSAGE-LABEL': label,
                                         'X-COILS-WORKFLOW-PROCESS-ID':    self.process.object_id
                                     } )
