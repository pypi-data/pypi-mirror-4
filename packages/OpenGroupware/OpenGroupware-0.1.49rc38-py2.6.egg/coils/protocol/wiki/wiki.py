#
# Copyright (c) 2012, 2013
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
from coils.core           import Document, NoSuchPathException, Project, Folder
from coils.net            import PathObject, Protocol
from wikipage             import WikiPage
from blobpage             import BLOBPage
from referralpage         import ReferralPage
from csspage              import CSSPage
from jspage               import JSPage

class Wiki(Protocol, PathObject):
    __pattern__   = [ '^wiki$' ]
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def get_name(self):
        return 'wiki'

    def is_public(self):
        return False

    def get_index_document_id(self):

        project = self.context.run_command( 'project::get', id=7000 )
        if project:
            document = self.context.run_command( 'project::get-path', path='/Wiki/index.markdown',
                                                                      project=project )
            if document:
                return document.object_id
        return None

    def lookup_index_document_from_folder( self, folder ):
        target = self.context.run_command( 'folder::ls', folder=folder, name='index.markdown' )
        if target:
            return target[ 0 ]
        target = self.context.run_command( 'folder::ls', folder=folder, name='index.txt' )
        if target:
            return target[ 0 ]
        return None

    def lookup_index_document_from_project( self, project ):
        return self.lookup_index_document_from_folder( project.folder )

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name == '.css':
            return CSSPage( self, name, request=self.request,
                                        parameters=self.parameters,
                                        context=self.context )
        elif name == '.js':
            return JSPage( self, name, request=self.request,
                                       parameters=self.parameters,
                                       context=self.context )        
        elif name.isdigit( ):
            target = self.context.type_manager.get_entity( long( name ) )
        else:
            # Name must refer to a project (by project "number")
            target = self.context.run_command( 'project::get', number=name )

        if target is None:
            raise NoSuchPathException( 'Wiki has no such page as "{0}"'.format( name ) )

        # Some targets bounce.  A project refers to the index.txt document in the root
        # folder of the project, if any.  A folder refers to the index.txt document
        # within itself, if any.
        if isinstance( target, Project ):
            target = self.lookup_index_document_from_project( target )
        elif isinstance( target, Folder ):
            target = self.lookup_index_document_from_folder( target )

        if isinstance( target, Document ):
            if target.mimetype == 'text/plain':
                return WikiPage( self, name, request=self.request,
                                             document=target,
                                             parameters=self.parameters,
                                             context=self.context )
            else:
                return BLOBPage( self, name, request=self.request,
                                             document=target,
                                             parameters=self.parameters,
                                             context=self.context )
        else:
            return ReferralPage( self, name, request=self.request,
                                             document=target,
                                             parameters=self.parameters,
                                             context=self.context )

    def do_HEAD(self):
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=self.entity.get_mimetype(type_map=self._mime_type_map),
                                     headers={ 'etag': self.get_property_getetag(),
                                               'Content-Length': str(self.entity.file_size) } )

    def do_GET(self):
        index_id = self.get_index_document_id( )
        if index_id:
            self.request.simple_response(301, data=None, headers={ 'Location': '/wiki/{0}'.format( index_id ), } )
        raise NoSuchPathException( 'Wiki has not index page.' )

    def do_POST(self):
        raise NotImplementedException('POST not supported by Wiki')

    def do_PUT(self, name):
        raise NotImplementedException('POST not supported by Wiki')
