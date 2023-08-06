#
# Copyright (c) 2012 Tauno Williams <awilliam@whitemice.org>
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
from StringIO             import StringIO
from coils.core           import *
from coils.net            import PathObject
from coils.net.ossf       import MarshallOSSFChain
from coils.foundation     import BLOBManager

class ProjectObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    #
    # Method Handlers
    #

    def get_file_name(self):
        return '{0}.txt'.format( self.entity.object_id )

    def get_etag(self):
        return '{0}:{1}'.format( self.entity.object_id, self.entity.version )

    def get_stream(self):
        document = self.context.run_command('project::get-path', project=self.entity, path='/index.txt')
        if document:
            rfile = self.context.run_command( 'document::get-handle', document=document )
            if rfile:
                return rfile

        if self.entity.comment:
            rfile = StringIO( )
            rfile.write( self.entity.comment )
            rfile.seek( 0 )
            return rfile

        return BLOBManager.ScratchFile( )

    def marshall(self):
        rfile = self.get_stream( )
        handle, mimetype = MarshallOSSFChain( rfile, 'text/plain', self.parameters )
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek( 0 )
        return handle, mimetype, size

    def do_HEAD(self):
        stream, mimetype, size = self.marshall( )
        self.request.simple_response( 200,
                                      data=None,
                                      mimetype=mimetype,
                                      headers={ 'etag': self.get_etag( ),
                                                'Content-Length': str( size ),
                                                'Content-Disposition': '{0}; filename={1}'.format(self.disposition, self.get_file_name( ) ), } )

    def do_GET(self):
        stream, mimetype, size = self.marshall( )
        self.request.simple_response( 200,
                                      stream=stream,
                                      mimetype=mimetype,
                                      headers={ 'etag': self.get_etag( ),
                                                'Content-Length': str( size ),
                                                'Content-Disposition': '{0}; filename={1}'.format(self.disposition, self.get_file_name( ) ), } )
        BLOBManager.Close( stream )

