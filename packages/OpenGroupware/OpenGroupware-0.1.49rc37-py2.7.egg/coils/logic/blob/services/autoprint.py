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
import uuid, cups
from coils.core       import *

global IPP_PRINTABLE_TYPES
global IPP_SERVER_NAME

class AutoPrintService(ThreadedService):
    __service__ = 'coils.blob.autoprint'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def setup(self, silent=True):
        '''
        Perform service setup and start all the registered threads.
        '''
        global IPP_PRINTABLE_TYPES
        global IPP_SERVER_NAME

        ThreadedService.setup( self, silent=silent )

        sd = ServerDefaultsManager( )
        IPP_PRINTABLE_TYPES = sd.default_as_list( 'IPPPrintableMIMETypes' )
        IPP_SERVER_NAME = sd.string_for_default( 'DefaultIPPServer', '127.0.0.1' )

        self._broker.subscribe( '{0}.{1}'.format( self.__service__, uuid.uuid4().hex ),
                                self.receive_message,
                                expiration=900000,
                                queue_type='fanout',
                                durable=False,
                                exchange_name='OpenGroupware_Coils_Notify' )

    def prepare(self):
        ThreadedService.prepare(self)

        self._ctx = AdministrativeContext( { }, broker=self._broker )

    #
    # Message Handlers
    #

    def do___audit_document(self, parameter, packet):

        global IPP_PRINTABLE_TYPES
        global IPP_SERVER_NAME

        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )
        print_queue = None

        if action_tag == '00_created':
            self.log.debug( 'Autoprint service attempting to queue OGo#{0} [Document]'.format( object_id ) )
            document = self._ctx.run_command( 'document::get', id=object_id )
            if not document:
                self.log.error( 'Unable to marshall OGo#{0} [Document]'.format( object_id ) )
                return

            if not document.folder_id:
                self.log.error( 'OGo#{0} [Document] is not assigned a folder'.format( object_id ) )
                return
            folder = self._ctx.run_command( 'folder::get', id=document.folder_id )
            if not folder:
                self.log.debug( 'Cannot marshall OGo#{0} [Folder]'.format( folder.object_id ) )
                return

            prop = self._ctx.property_manager.get_property( folder, 'http://www.opengroupware.us/autoprint', 'autoPrintQueue' )
            if prop:
                print_queue = prop.get_value( )
            if not print_queue:
                return

            if print_queue:
                self.log.debug( 'Autoprint for new document in OGo#{0} [Folder] targeted to "{1}"'.format( folder.object_id, print_queue ) )
                mimetype = self._ctx.type_manager.get_mimetype( document )
                if mimetype in IPP_PRINTABLE_TYPES:
                    try:
                        rfile = self._ctx.run_command( 'document::get-handle', document=document )
                        if rfile:
                            cups.setServer( IPP_SERVER_NAME )
                            ipp_connection = cups.Connection( )
                            ipp_connection.printFile( print_queue, rfile.name, document.get_file_name( ), { 'media': 'Letter',
                                                                                                            'fit-to-page': str( 'yes' ), } )
                            BLOBManager.Close( rfile )
                            ipp_connection = None
                    except Exception as e:
                        self.log.exception( e )
                else:
                    self.log.info( 'Document created in autoprint folder of an unprintable type "{0}"'.format( mimetype ) )

