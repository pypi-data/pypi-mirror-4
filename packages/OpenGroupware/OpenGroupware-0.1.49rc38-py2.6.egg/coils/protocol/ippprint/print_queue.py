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

from document_print       import DocumentPrint

ENTITY_PRINT_HANDLERS = { 'document': DocumentPrint, }


class PrintQueue(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__( self, parent, **params )

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        object_id = long( name )
        kind = self.context.type_manager.get_type( object_id )
        processor = ENTITY_PRINT_HANDLERS.get( kind.lower( ), None )
        if processor:
            entity = self.context.type_manager.get_entity( object_id )
            if entity:
                return processor(self, name, request=self.request,
                                             parameters=self.parameters,
                                             context=self.context,
                                             entity=entity,
                                             ipp_connection=self.ipp_connection )
        else:
            raise NotSupportedException( 'IPP printing not implemented for entity type "{0}"'.format( kind ) )

        raise NoSuchPathException( 'No such path' )


    def do_GET(self):
        raise NotImplementedException( 'GET operation not implmented on PrintQueue' )
