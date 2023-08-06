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
#
import uuid
from coils.core       import *


from thumbnail_image import ThumbnailImage
from thumbnail_pdf import ThumbnailPDF

AUTOTHUMBNAILER_VERSION=101

THUMBERS = { 'image/jpeg':       ThumbnailImage,
             'image/png':        ThumbnailImage,
             'application/pdf' : ThumbnailPDF,  }

class AutoThumbService(ThreadedService):
    __service__ = 'coils.blob.autothumb'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def setup(self, silent=True):
        ThreadedService.setup( self, silent=silent )

        self._broker.subscribe( '{0}.{1}'.format( self.__service__, uuid.uuid4().hex ),
                                self.receive_message,
                                expiration=900000,
                                queue_type='fanout',
                                durable=False,
                                exchange_name='OpenGroupware_Coils_Notify' )

    def prepare(self):
        ThreadedService.prepare(self)

        self._ctx = AdministrativeContext( { }, broker=self._broker )

    def thumbnail_document(self, object_id):
        document = self._ctx.run_command( 'document::get', id=object_id )
        if not document:
            self.log.debug( 'Unable to marshall OGo#{0} [Document] for thumbnailing'.format( object_id ) )
            return
        self.log.debug( 'Autothumb service attempting to thumbnail OGo#{0} [Document]'.format( object_id ) )

        filename = '{0}.{1}.{2}.thumb'.format( document.object_id, AUTOTHUMBNAILER_VERSION, document.version )
        filename = 'cache/thumbnails/{0}/{1}/{2}'.format( filename[1:2], filename[2:3], filename )

        # TODO: If the current thumbnail exists, do not recaclulate

        mimetype = self._ctx.type_manager.get_mimetype( document )
        thumber = THUMBERS.get( mimetype, None )
        if thumber:
            thumber = thumber( self._ctx, mimetype, document, filename )
            try:
                if thumber.create( ):
                    self.log.debug( 'Thumbnail created for OGo#{0} [Document] of type "{1}"'.format( object_id, mimetype ) )
            except:
                self.log.debug( 'Thumbnail creation failed for OGo#{0} [Document] of type "{1}"'.format( object_id, mimetype ) )
            finally:
                thumber = None

    #
    # Message Handlers
    #

    def do___audit_document(self, parameter, packet):

        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )

        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass

        #This some type of change, recalculate the thumbnail

        self.thumbnail_document( object_id )

        # TODO: Delete any now expire thumbnails

    def do_process_since(self, parameter, packet):

        object_id = long( packet.data.get( 'objectId', 0 ) )

        db = self._ctx.db_session( )
        query = db.query( Document.object_id ).filter( Document.object_id > object_id )
        for result in query.all( ):
            self.thumbnail_document( result[ 0 ] )

    def do_thumbnail(self, parameter, packet):

        self.thumbnail_document( long( parameter ) )
