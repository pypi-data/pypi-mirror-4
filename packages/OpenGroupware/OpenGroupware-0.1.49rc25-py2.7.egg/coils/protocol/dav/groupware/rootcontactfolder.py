#
# Copyright (c) 2009, 2011, 2012
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
from coils.core                        import *
from coils.foundation                  import CTag, Contact
from coils.net                         import DAVFolder, \
                                              Parser, \
                                              Multistatus_Response, \
                                              DAVObject, \
                                              OmphalosCollection, \
                                              OmphalosObject

from groupwarefolder                   import GroupwareFolder

from coils.protocol.dav.managers       import DAVContactManager, mimestring_to_format

from accountsfolder                    import AccountsFolder
from favoritecontactsfolder            import FavoriteContactsFolder
from projectcontactsfolder             import ProjectContactsFolder
from personalcontactsfolder            import PersonalContactsFolder
from allcontactsfolder                 import AllContactsFolder
from addressbookfolder                 import AddressBookFolder


RESERVED_ADDRESSBOOK_NAMES = [ 'All Contacts', 'Users', 'Favorites', 'Personal' ]

class RootContactFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self.manager = DAVContactManager( context=self.context )

    @property
    def managed_entity(self):
        return 'Contact'

    def supports_DELETE(self):
        return True

    def __repr__(self):
        return '<RootContactsFolder name="{0}"/>'.format(self.name)

    def _load_contents(self):
        self.insert_child( 'Favorites', FavoriteContactsFolder( self, 'Favorites', request=self.request, context=self.context, ) )
        if self.context.user_agent_description[ 'webdav' ][ 'showContactsAllFolder' ]:
            self.insert_child( 'All Contacts', AllContactsFolder( self, 'All Contacts', request=self.request, context=self.context, ) )
        if self.context.user_agent_description[ 'webdav' ][ 'showContactsUsersFolder' ]:
            self.insert_child( 'Users', AccountsFolder( self, 'Users', request=self.request, context=self.context, ) )
        # Load collection addressbooks
        for collection in [ x for x in self.context.run_command( 'collection::list', properties=[Collection] ) if x.kind == ':addressbook' ]:
            # TODO: Deal with duplicate names!
            self.insert_child( collection.title, AddressBookFolder( self, collection.title, entity=collection, request=self.request, context=self.context ) )
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        if name.startswith( '.' ):
            function_name = 'render_key_{0}'.format( name[ 1: ].lower().replace( '.', '_' ) )
            if hasattr( self, function_name ):
                return getattr( self, function_name )( name, is_webdav=is_webdav, auto_load_enabled=auto_load_enabled )
            else:
                self.no_such_path( )
        else:
            format = mimestring_to_format( self.request.headers.get( 'Content-Type', None ), default_format='ics' )
            if self.load_contents( ):
                child = self.get_child( name )

            if not child:
                child = self.manager.find( name, self.request.headers.get( 'Content-Type', None ) )

            if isinstance( child, DAVFolder ):
                return child
            elif child is not None:
                return self.get_entity_representation( name, child, location=None,
                                                                    representation = format,
                                                                    is_webdav=is_webdav )

        self.no_such_path( )

    def do_REPORT(self):
        ''' Preocess a report request '''
        payload = self.request.get_request_payload()
        self.log.debug('REPORT REQUEST: %s' % payload)
        parser = Parser.report(payload, self.context.user_agent_description)
        if parser.report_name == 'principal-match':
            # Just inclue all contacts, principal-match REPORTs are misguided
            self.load_contents( )
            resources = [ ]
            for child in self.get_children( ):
                if isinstance( child, Contact ):
                    name = child.get_file_name( )
                    resources.append( self.get_entity_representation( name, child, location=None,
                                                                                   representation = 'ics',
                                                                                   is_webdav=True ) )

                elif isinstance( child, DAVFolder ):
                    resources.append( child )

            stream = StringIO()
            properties, namespaces = parser.properties
            Multistatus_Response( resources=resources,
                                  properties=properties,
                                  namespaces=namespaces,
                                  stream=stream )
            self.request.simple_response( 207,
                                          data=stream.getvalue( ),
                                          mimetype='text/xml; charset="utf-8"' )
        else:
            raise NotImplementedException('REPORT {0} not supported by ContactsFolder'.format( parser.report_name ) )

    #
    # OPTIONS
    #

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'OPTIONS',   'GET',       'HEAD',  'MKCOL',
                    'TRACE', 'COPY', 'MOVE',  'PROPFIND', 'PROPPATCH', 'LOCK', 'UNLOCK',
                    'REPORT', 'ACL',  ]
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=u'text/plain',
                                     headers={ 'DAV':           '1, 2, access-control',
                                               'Allow':         ','.join(methods),
                                               'Connection':    'close',
                                               'MS-Author-Via': 'DAV'} )

    #
    # MKCOL
    #

    def do_MKCOL(self, name):
        ''' Create an addressbook collection with the specified name. '''

        if name in RESERVED_ADDRESSBOOK_NAMES:
            raise AccessForbiddenException( 'Attempt to use reserved name for addressbook collection' )

        self.load_contents( )
        if self.get_child( name ):
            raise AccessForbiddenException( 'An address book by the name of "{0}" already exists'.format( name ) )

        collection = self.context.run_command( 'collection::new', values = { 'name': name,
                                                                             'kind': ':addressbook',
                                                                             'davenabled': 1, } )
        self.context.commit( )
        self.request.simple_response( 201 )


    #
    # MOVE
    #

    def do_MOVE(self, name):

        source, target, target_name, overwrite = self.move_helper(name)

        if target == self and source.entity:

            if target_name in RESERVED_ADDRESSBOOK_NAMES:
                raise AccessForbiddenException( 'Attempt to use reserved name for addressbook.' )

            print source, source.entity
            if isinstance(source.entity, Collection):
                try:
                    sink = self.get_object_for_key( target_name )
                except NoSuchPathException:
                    print 'NO SUCH PATH'
                    target = self.context.run_command( 'collection::set', object=source.entity,
                                                                          values={ 'name': target_name } )

                    self.context.commit( ) # COMMIT
                    self.request.simple_response(201)
                    return
                else:
                    raise AccessForbiddenException( 'An addresbook of the specified name "{0}" already exists'.format( target_name ) )

        raise NotImplementedException()

    #
    # DELETE
    #

    def do_DELETE(self, name):

        if name in RESERVED_ADDRESSBOOK_NAMES:
            raise AccessForbiddenException( 'Deletion of "{0}" is not permitted'.format( name ) )

        self.load_contents( )
        
        target = self.get_child( name )
        if target:
            if isinstance( target, AddressBookFolder ):
                collection = target.entity
                self.context.run_command( 'collection::delete', object=collection )
                self.context.commit( )
                self.request.simple_response( 204 )
                return
            else:
                raise NotImplementedException()
        else:
            self.no_such_path( )
