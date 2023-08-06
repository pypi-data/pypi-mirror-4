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
import uuid, cups
from coils.core           import *
from coils.net            import PathObject

#TODO: Load these from a server default

class DocumentPrint(PathObject):

    PRINTABLE_TYPES = None

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__( self, parent, **params )
        if not DocumentPrint.PRINTABLE_TYPES:
            DocumentPrint.PRINTABLE_TYPES = ServerDefaultsManager().default_as_list( 'IPPPrintableMIMETypes' )

    def parse_parameters(self):
        #TODO: Are there more options? especially if it is a text document?
        options = { 'media': self.parameters.get( 'mediasize', [ 'Letter', ] )[ 0 ] }
        if 'fittopage' in self.parameters:
            options[ 'fit-to-page' ] = str( 'yes' )
        return options

    def generate_job_name(self):
        return '{0}@{1}'.format( uuid.uuid4().hex, self.context.cluster_id )

    def do_GET(self):

        mimetype = self.context.type_manager.get_mimetype( self.entity )

        if mimetype in DocumentPrint.PRINTABLE_TYPES:

            rfile = self.context.run_command( 'document::get-handle', document=self.entity )
            if rfile:
                job_name = self.generate_job_name( )
                self.ipp_connection.printFile( self.parent.name, rfile.name, job_name, self.parse_parameters( ) )
                BLOBManager.Close( rfile )
                self.request.simple_response( 200, mimetype='text/plain', data=job_name )
            else:
                raise CoilsException( 'Unable to marshal handle for OGo#{0}'.format( self.entity.object_id ) )
        else:
            raise NotImplementedException( 'Documents of type "{0}" cannot be queued'.format( mimetype ) )
