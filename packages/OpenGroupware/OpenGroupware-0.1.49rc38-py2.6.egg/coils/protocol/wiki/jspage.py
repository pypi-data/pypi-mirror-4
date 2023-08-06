#
# Copyright (c) 2013
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

class JSPage(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)
        self.document = params.get( 'document', None )
        if not self.document:
            self.project = self.context.run_command( 'project::get', id=7000 )
        else:
            self.project = None

    def get_content_handle(self):
        if self.document:
            handle = self.context.run_command( 'document::get-handle', id=self.document.object_id )
            if handle:
                return self.document.checksum, handle
        return None, None

    #
    # Method Handlers
    #

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if self.document:
            return self
        if self.project and name.endswith( '.js' ):
            document = self.context.run_command( 'project::get-path', path='/Wiki/{0}'.format( name ),
                                                                      access_check=False,
                                                                      project=self.project )
            if document:
                return JSPage( self, name, request=self.request,
                                           document=document,
                                           parameters=self.parameters,
                                           context=self.context )
        raise NoSuchPathException( 'No such script file available.' )
            
    def do_HEAD(self):
        if self.document:
            self.request.stream_response( 204, data=None, mimetype='text/javascript',
                                               headers={ 'etag': document.checksum } )
        else:
            self.request.stream_response( 204, data=None )

    def do_GET(self):
        checksum, handle = self.get_content_handle( )
        if handle:
            self.request.stream_response( 200, stream=handle, mimetype='text/javascript',
                                               headers={ 'etag': checksum } )
            BLOBManager.Close(handle)
            return
        raise NoSuchPathException( 'No style sheet available' )
