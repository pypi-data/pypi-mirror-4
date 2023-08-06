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

from coils.logic.blob import AUTOTHUMBNAILER_VERSION
CACHE_MAX_AGE=60480

class DocumentThumb(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__( self, parent, **params )

    @property
    def thumbnail_path(self):
        filename = '{0}.{1}.{2}.thumb'.format( self.entity.object_id, AUTOTHUMBNAILER_VERSION, self.entity.version )
        return 'cache/thumbnails/{0}/{1}/{2}'.format( filename[1:2], filename[2:3], filename )

    def get_etag(self, document):
        return '{0}:{1}:{2}:png'.format( document.object_id, document.version, AUTOTHUMBNAILER_VERSION )

    def get_filename(self, document):
        return '{0}.{1}.{2}.png'.format( document.object_id, document.version, AUTOTHUMBNAILER_VERSION )

    def get_thumbnail(self):

        rfile = BLOBManager.Open( self.thumbnail_path, 'r', encoding='binary' )
        if rfile:
            return rfile, self.get_etag( self.entity ), self.get_filename( self.entity )

        project = self.context.run_command( 'project::get', id=7000, access_check=False )
        if not project:
            return None, self.get_etag( self.entity ), self.get_filename( self.entity )

        mimetype = self.context.type_manager.get_mimetype( self.entity )
        filename = mimetype.replace( '/', '-' )
        document = self.context.run_command( 'project::get-path', path='/Thumbnails/{0}.png'.format( filename ),
                                                                  project=project,
                                                                  access_check=False )
        if not document:
            self.log.debug( 'No icon configured MIME type "{0}"'.format( mimetype ) )
            document = self.context.run_command( 'project::get-path', path='/Thumbnails/application-octet-stream.png',
                                                                      project=project,
                                                                      access_check=False )
        if document:
            handle = self.context.run_command( 'document::get-handle', document=document )
            return handle, self.get_etag( document ), self.get_filename( document )
        else:
            self.log.debug( 'No default application/octet-stream icon found' )
        return None, None, None

    def do_HEAD(self):
        handle, etag, filename = self.get_thumbnail( )
        if not handle:
            raise NoSuchPathException( 'No thumbnail available for OGo#{0}'.format( self.entity.object_id ) )
        self.request.simple_response( 200,
                                      data=None,
                                      mimetype='image/png',
                                      headers={ 'Content-Disposition': 'inline; filename={0}'.format( filename ),
                                                'Cache-Control': 'max-age={0}'.format( CACHE_MAX_AGE ),
                                                'etag': etag } )
        BLOBManager.Close( handle )

    def do_GET(self):

        handle, etag, filename = self.get_thumbnail( )

        if not handle:
            raise NoSuchPathException( 'No thumbnail available for OGo#{0}'.format( self.entity.object_id ) )

        # If the client provided us with an etag, let us check it so we may get
        # luck and return a 304-no-content-change-request
        client_etag = self.request.headers.get( 'If-None-Match', None )
        if client_etag:
            if client_etag == etag:
                self.request.simple_response(304,
                                     data=None,
                                     mimetype='image/png',
                                     headers={ 'Content-Disposition': 'inline; filename={0}'.format( filename ),
                                               'Cache-Control': 'max-age={0}'.format( CACHE_MAX_AGE ),
                                               'etag': etag } )
                return

        self.request.stream_response(200,
                                     stream=handle,
                                     mimetype='image/png',
                                     headers={ 'Content-Disposition': 'inline; filename={0}'.format( filename ),
                                               'Cache-Control': 'max-age={0}'.format( CACHE_MAX_AGE ),
                                               'etag': etag } )

        BLOBManager.Close( handle )
