#
# Copyright (c) 2011, 2013
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
from coils.net            import PathObject, Protocol
from document_thumb       import DocumentThumb
from folder_thumb         import FolderThumb
from unknown_thumb        import UnknownThumb

ENTITY_TYPE_TO_THUMBER = { 'folder':   FolderThumb,
                           'document': DocumentThumb,
                           'file':     DocumentThumb, }

from coils.logic.blob import AUTOTHUMBNAILER_VERSION

class Thumb(Protocol, PathObject):
    __pattern__   = [ 'thumb', ]
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def get_name(self):
        return 'thumbnail'

    def is_public(self):
        return False

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        object_id = long( name )
        kind = self.context.type_manager.get_type( object_id )
        if kind.lower( ) in ( 'unknown', ):
            return UnknownThumb(self, name, request=self.request,
                                             parameters=self.parameters,
                                             context=self.context, )
        thumber = ENTITY_TYPE_TO_THUMBER.get( kind.lower( ), None )
        if thumber:
            entity = self.context.type_manager.get_entity( object_id )
            if entity:
                return thumber(self, name, request=self.request,
                                           parameters=self.parameters,
                                           context=self.context,
                                           entity=entity )
        else:
            raise NotSupportedException( 'Thumbnails not implemented for entity type "{0}"'.format( kind ) )

        raise NoSuchPathException( 'No such path' )

    def do_GET(self):
        self.request.simple_response( 200, data='Context is {0}'.format( self.context ) )

    def do_POST(self):
        raise NotImplementedException( 'POST not supported by Thumbnail protocol' )
