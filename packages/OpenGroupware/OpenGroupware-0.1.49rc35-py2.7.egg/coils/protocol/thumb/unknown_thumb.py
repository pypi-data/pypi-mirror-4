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
from thumb_fallback       import ThumbnailFallback

THUMBNAILER_VERSION=100

class UnknownThumb(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__( self, parent, **params )

    def get_etag(self):
        return '{0}:{1}:png'.format( self.name.strip( ), THUMBNAILER_VERSION )

    def get_filename(self):
        return '{0}.{1}.png'.format( self.name.strip(), THUMBNAILER_VERSION )

    def get_thumbnail(self):

        project = self.context.run_command( 'project::get', id=7000, access_check=False )
        if project:
            document = self.context.run_command( 'project::get-path', path='/Thumbnails/application-x-opengroupware-error.png',
                                                                      project=project,
                                                                      access_check=False )
            if document:
                rfile = self.context.run_command( 'document::get-handle', document=document )
                if rfile:
                    return rfile

        return None

    def do_HEAD(self):
        self.request.simple_response(200,
                                     data=None,
                                     mimetype='image/png',
                                     headers={ 'etag':  self.get_etag( ) } )

    def do_GET(self):

        # If the client provided us with an etag, let us check it so we may get
        # luck and return a 304-no-content-change-request
        etag = self.request.headers.get( 'If-None-Match', None )
        if etag:
            if etag == self.get_etag( ):
                self.request.simple_response(304,
                                     data=None,
                                     mimetype='image/png',
                                     headers={ 'etag':  self.get_etag( ) } )
                return

        rfile = self.get_thumbnail( )
        if not rfile:
            raise NoSuchPathException( 'No thumbnail available for unknown entity' )

        # Expected cache life-time of a thumbnail is one week
        self.request.stream_response(200,
                                     stream=rfile,
                                     mimetype='image/png',
                                     headers={ 'Content-Disposition': 'inline; filename={0}'.format( self.get_filename( ) ),
                                               'Cache-Control': 'max-age=60480',
                                               'etag': self.get_etag( ) } )

        BLOBManager.Close( rfile )
