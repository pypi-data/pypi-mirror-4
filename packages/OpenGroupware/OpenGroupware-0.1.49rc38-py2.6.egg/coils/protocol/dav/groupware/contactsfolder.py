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
import sys, coils.core, time
from StringIO                          import StringIO
from coils.core                        import *
from coils.core.vcard                  import Parser as VCard_Parser
from coils.foundation                  import CTag, Contact
from coils.net                         import DAVFolder, \
                                              Parser, \
                                              Multistatus_Response, \
                                              DAVObject, \
                                              OmphalosCollection, \
                                              OmphalosObject
from groupwarefolder                   import GroupwareFolder
from accountsfolder                    import AccountsFolder
from coils.core.vcard                  import Parser as VCard_Parser

MIMESTRING_TO_FORMAT = { 'text/calendar': 'vcf',
                         'text/vcard':    'vcf',
                         'text/json':     'json',
                         'text/yaml':     'yaml',
                         'text/xml':      'xml',  }
            
def mimestring_to_format( mimestring ):
    if mimestring:
        return MIMESTRING_TO_FORMAT.get( mimestring.lower( ), 'vcf' )
    return 'vcf'

class ContactsFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        self.mode = 'all'
        DAVFolder.__init__(self, parent, name, **params)

    @property
    def managed_entity(self):
        return 'Contact'

    def __repr__(self):
        return '<ContactsFolder name="{0}" projectMode="{1}" favoriteMode="{2}"/>'.\
            format(self.name, self.is_project_folder, self.is_favorites_folder)

    def supports_GET(self):
        return False

    def supports_POST(self):
        return False

    def supports_PUT(self):
        return True

    def supports_DELETE(self):
        return True

    def supports_PROPFIND(self):
        return True

    def supports_PROPATCH(self):
        return False

    def supports_MKCOL(self):
        return False

    # PROP: RESOURSETYPE
    def get_property_webdav_resourcetype(self):
        ''' 
            Return the resource type of the collection, which is always
            'collection'. See RFC2518, Section 13.9'''

        if self.is_root_folder:
            return u'<D:collection/>'
        else:
            return u'<D:collection/><E:addressbook/>'

    # PROP: GETCTAG

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_carddav_supported_address_data(self):
         return u'<E:address-data-type content-type="text/vcard" version="3.0"/>'

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    '''
    def get_property_webdav_displayname(self):
        if self.is_project_folder:
            return self.project.number
        elif self.is_favorites_folder:
            return u'Favorite Contacts'
        else:
            return u'All Contacts'
    '''

    def get_ctag(self):
        if (self.is_collection_folder):
            return self.get_ctag_for_collection()
        else:
            return self.get_ctag_for_entity('Person')

    @property
    def is_root_folder(self):
        if self.parent.name == 'dav':
            return True
        return False

    @property
    def is_favorites_folder(self):
        if self.mode == 'favorites':
            return True
        return False
        
    @property
    def is_all_folder(self):
        if self.mode == 'all':
            return True
        return False

    def _load_contents(self):
        
        if self.is_root_folder:
            self.insert_child( 'Favorites', ContactsFolder( self, 'Favorites', request=self.request, context=self.context, mode='favorites' ) )
            if self.context.user_agent_description[ 'webdav' ][ 'showContactsAllFolder' ]:
                self.insert_child( 'All',       ContactsFolder( self, 'All', request=self.request, context=self.context, mode='all' ) )
            if self.context.user_agent_description[ 'webdav' ][ 'showContactsUsersFolder' ]:
                self.insert_child( 'Users',       AccountsFolder( self, 'Users', request=self.request, context=self.context, ) )
            return True
            
        if self.is_project_folder:
            # Project sub-folder (all contacts assigned to the project)
            content = self.context.run_command('project::get-contacts', object=self.entity)
        elif self.is_favorites_folder:
            # Favorites folder
            content = self.context.run_command('contact::get-favorite')
        elif self.is_all_folder:
            # Load *ALL* available contacts - this could be BIG!
            content = self.context.run_command('contact::list', properties = [ Contact ])
            
        if (len(content) > 0):
            for contact in content:
                self.insert_child( contact.object_id, contact, alias=contact.get_file_name( ) )
        else:
            self.empty_content()
            
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name.startswith( '.' ):
            function_name = 'render_key_{0}'.format( name[ 1: ].lower().replace( '.', '_' ) )
            if hasattr( self, function_name ):
                return getattr( self, function_name )( name, is_webdav=is_webdav, auto_load_enabled=auto_load_enabled )
            else:
                self.no_such_path( )
        else:
            format, extension, uid, object_id = self.inspect_name( name, default_format = 'ics' )
            if self.is_collection_folder or self.is_root_folder:
                if ( self.load_contents( ) and ( auto_load_enabled ) ):
                    child = self.get_child( name )
            
            if not child:                
                child = self.context.run_command( 'contact::get', uid=uid, href=name )
                if not child and object_id:
                    child = self.context.run_command( 'contact::get', id=object_id)

            if isinstance( child, DAVFolder ):
                return child
            elif child is not None:
                return self.get_entity_representation( name, child, location=None,
                                                                    representation = format,
                                                                    is_webdav=is_webdav )
                                                                      
        self.no_such_path( )

    def apply_permissions(self, contact):

        pass

    def do_PUT(self, name):
        
        if_etag = self.request.headers.get('If-Match', None)
        if (if_etag is None):
            self.log.warn('Client issued a put operation with no If-Match!')
        else:
            # TODO: Implement If-Match test
            self.log.warn('If-Match test not implemented at {0}'.format(self.url))
        
        format = mimestring_to_format( self.request.headers.get( 'Content-Type', None ) )
        format, extension, uid, object_id = self.inspect_name( name, default_format = format)
        payload = self.request.get_request_payload( )
        if format == 'ics':
            payload = VCard_Parser.Parse( payload, self.context )
        else:
            raise NotImplementedException( 'PUT of object format "{0}" not implemented'.format( format ) )

        if len( payload ) == 1:
            payload = payload[ 0 ]
            
            if object_id:    
                contact = self.context.run_command( 'contact::get', id=object_id )
            else:
                contact = self.context.run_command( 'contact::get', uid=uid, href=name) 

            if not contact:
                # Create
                contact = self.context.run_command( 'contact::new', values=payload )
                contact.href = name
                self.apply_permissions( contact )

                if self.is_favorites_folder:
                    # Contact is being created in the favorites folder, automatically add favorite status
                    self.context.run_command( 'contact::add-favorite', id=contact.object_id )

                elif self.is_project_folder:
                    self.context.run_command( 'project::assign-contact', project=self.entity, 
                                                                         contact_id = contact.object_id )
                    raise NotImplementedException( 'Creating contacts via a project folder is not implemented.' )

                self.context.commit( )
                self.request.simple_response( 201,
                                              data=None,
                                              mimetype=u'text/x-vcard; charset=utf-8',
                                              headers={ 'Etag':     u'{0}:{1}'.format(contact.object_id, contact.version),
                                                        'Location': '/dav/Contacts/{0}'.format(contact.get_file_name( ) ) } )

            else:
                # Update
                # TODO: Check If-Match
                try:
                    contact = self.context.run_command( 'contact::set', object=contact, values=payload )
                    if self.is_favorites_folder:
                        # Contact is being updated in the favorites folder, automatically add favorite status
                        # This means every update to a favorite contact causes a user defaults rewrite
                        self.context.run_command( 'contact::add-favorite', id=contact.object_id )

                    elif self.is_project_folder:
                        # TODO: Implement: Update contacts via a project sub-folder
                        self.context.run_command( 'project::assign-contact', project=self.entity, 
                                                                             contact_id = contact.object_id )

                except Exception, e:
                    self.log.error( 'Error updating objectId#{0} via WebDAV'.format( object_id ) )
                    self.log.exception( e )
                    raise e
                else:
                    self.context.commit( )
                    self.request.simple_response( 204,
                                                  data=None,
                                                  mimetype=u'text/x-vcard; charset=utf-8',
                                                  headers={ 'Etag':     u'{0}:{1}'.format( contact.object_id, contact.version ),
                                                            'Location': '/dav/Contacts/{0}'.format( contact.get_file_name( ) ) } )

    def do_DELETE(self, name):

        format, extension, uid, object_id = self.inspect_name( name, default_format = 'ics' )

        if ( self.is_favorites_folder and ( self.load_contents( ) ) ):
            contact = self.get_child( name )
        else:
            contact = self.context.run_command( 'contact::get', uid=uid, href=name )
            if not contact and object_id:
                contact = self.context.run_command( 'contact::get', id=object_id )
 
        if not contact:
            self.no_such_path()

        try:

            if self.is_favorites_folder:
                # NOTE: Deletion of a contact from a favorite folder does *not* delete
                #       the contact it merely removes the favorite status.
                self.log.debug( 'Removing favorite status from contactId#{0} for userId#{1}'.\
                    format( contact.object_id, self.context.account_id ) )
                self.context.run_command( 'contact::remove-favorite', id=contact.object_id )

            elif self.is_project_folder:
                # NOTE: Deletion of a contact from a projects folder should *not* delete
                #       the contact only unassign the contact from the project.
                self.context.run_command( 'project::unassign-contact', project = self.entity, 
                                                                       contact_id = contact.object_id )

            else:
                # Delete the contact
                if contact.is_account:
                    self.simple_response( 423, message='Account objects cannot be deleted.' )
                    return
                    
                self.context.run_command( 'contact::delete', object=contact )

            self.context.commit( )
        except Exception, e:
            self.log.exception( e )
            self.request.simple_response( 500, message='Deletion failed' )
        else:
            self.request.simple_response( 204 )

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

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'OPTIONS',   'GET',       'HEAD',     'POST',      'PUT',  'DELETE', 
                    'TRACE', 'COPY', 'MOVE',  'PROPFIND', 'PROPPATCH', 'LOCK', 'UNLOCK', 
                    'REPORT', 'ACL',  ]
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=u'text/plain',
                                     headers={ 'DAV':           '1, 2, access-control, addressbook',
                                               'Allow':         ','.join(methods),
                                               'Connection':    'close',
                                               'MS-Author-Via': 'DAV'} )
