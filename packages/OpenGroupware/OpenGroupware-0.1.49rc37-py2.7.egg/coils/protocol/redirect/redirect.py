#
# Copyright (c) 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
import socket, yaml, traceback
from coils.core           import AdministrativeContext, \
                                 NoSuchPathException, \
                                 ObjectInfo, \
                                 CoilsException
from coils.net            import PathObject, Protocol


class Redirector(Protocol, PathObject):
    __pattern__   = [ '^redirect$', '^r$' ]
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def get_name(self):
        return 'redirect'

    def is_public(self):
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        redirect_to = None
        if name.isdigit( ):
            object_id = long( name )
            redirect_to = self.object_redirection( object_id )
        else:
            # TODO: Redirect aliases?
            pass

        if redirect_to:
            self.request.simple_response(301, headers={'Location': redirect_to}, data=None)
        else:
            raise NoSuchPathException( 'Redirector has no target for specified name.' )

    def do_HEAD(self):
        self.request.simple_response(204)

    def do_GET(self):
        # TODO: implement root page
        self.request.simple_response(204)

    def load_redirection_dictionary(self):
        redirector_map = { }
        project = self.context.run_command( 'project::get', id=7000, access_check=False )
        print project
        if project:
            document = self.context.run_command( 'project::get-path', path='/Sites/RedirectorMap.yaml',
                                                                      access_check=False,
                                                                      project=project )                                                                      
            if document:
                print document
                handle = self.context.run_command( 'document::get-handle', id=document.object_id )
                try:
                    redirector_map = yaml.load( handle )
                except Exception as e:
                    self.log.exception(e)
                    self.log.error( 'Redirector map is corrupt.' )
                    if self.context.amq_available:
                        self.context.send_administrative_notice( category='configuration',
                                                                 urgency=7,
                                                                 subject='Link Redirector Map Is Corrupt',
                                                                 message=traceback.format_exc( ) )

        return redirector_map

    def object_redirection(self, object_id):
        kind = None
        db = self.context.db_session()
        query = db.query( ObjectInfo ).filter( ObjectInfo.object_id == object_id )
        result = query.all( )
        if result:
            result = result[ 0 ]
            kind = ObjectInfo.translate_kind_from_legacy(result.kind ).lower( )

        if kind is None:
            raise NoSuchPathException( 'Redirector has no redirect for specified object.' )

        REDIRECT_DICT = self.load_redirection_dictionary( )
        if not REDIRECT_DICT:
            raise CoilsException( 'Entity redirector map not provisioned.' )

        # Determine Origin
        origin = '__default__'
        client_ip =  self.context._meta['connection']['client_address']
        # TODO: I suppose there should be some async or timeout-safe way to call this
        client_name = socket.gethostbyaddr( client_ip )
        if client_name:
            client_name = client_name[0].lower( )
            if client_name not in REDIRECT_DICT[ '__origins__' ]:
                client_name = '.'.join( client_name.split( '.' )[1:] )
            origin = REDIRECT_DICT[ '__origins__' ].get( client_name, '__default__' )

        redirect_to = REDIRECT_DICT[ origin ].get( kind, None )
        if redirect_to:
            return redirect_to.format( object_id )
        return None
