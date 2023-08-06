#
# Copyright (c) 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core           import *
from coils.net            import PathObject
from coils.net.ossf       import MarshallOSSFChain

class BLOBPage(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    #
    # Method Handlers
    #

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        return self

    def do_HEAD(self):
        # TODO: Check for locks!
        # TODO: What if the document doesn't report a mime-type?
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=document.mimetype,
                                     headers={ 'etag': '{0}:{1}'.format(self.entity.object_id,
                                                                        self.entity.version),
                                               'X-OpenGroupware-Filename': self.entity.get_display_name(),
                                               'Content-Length': str(self.entity.file_size) } )

    def do_GET(self):
        # TODO: Check for locks!
        # TODO: What if the document doesn't report a mime-type?
        handle = self.context.run_command('document::get-handle', id=self.document.object_id)
        handle, mimetype = MarshallOSSFChain(handle, 'text/plain', self.parameters)
        self.log.debug('MIME-Type after OSSF processing is {0}'.format(mimetype))
        self.context.run_command('document::record-download', document=self.document)
        self.context.commit()
        self.request.stream_response(200,
                                     stream=handle,
                                     mimetype=mimetype,
                                     headers={ 'Content-Disposition': 'attachment; filename={0}'.format( self.document.get_display_name( ) ),
                                               'X-OpenGroupware-Filename': self.document.get_display_name(),
                                               'etag': '{0}:{1}'.format(self.document.object_id,
                                                                        self.document.version) } )
        BLOBManager.Close(handle)
