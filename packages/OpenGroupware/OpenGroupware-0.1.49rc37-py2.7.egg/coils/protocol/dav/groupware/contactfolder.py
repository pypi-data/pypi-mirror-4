#
# Copyright (c) 2009, 2011, 2012, 2013
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
from coils.protocol.dav.managers       import DAVContactManager, mimestring_to_format


class ContactFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self.manager = DAVContactManager( context=self.context )
        self.enable_find_in_object_for_key = True

    @property
    def managed_entity(self):
        return 'Contact'

    def supports_PUT(self):
        return True

    def supports_DELETE(self):
        return True

    def supports_PROPFIND(self):
        return True

    #
    # PROPERTIES
    #

    # PROP: GETCTAG

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    def get_ctag(self):
        if (self.is_collection_folder):
            return self.get_ctag_for_collection()
        else:
            return self.get_ctag_for_entity('Person')

    #
    # OBJECT FOR KEY
    #

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        if name.startswith( '.' ):
            function_name = 'render_key_{0}'.format( name[ 1: ].lower().replace( '.', '_' ) )
            if hasattr( self, function_name ):
                return getattr( self, function_name )( name, is_webdav=is_webdav, auto_load_enabled=auto_load_enabled )
            else:
                self.no_such_path( )
        else:
            format = mimestring_to_format( self.request.headers.get( 'Content-Type', None ), default_format='ics' )
            child = None
            if ( self.load_contents( ) and ( auto_load_enabled ) ):
                child = self.get_child( name )

            if not child and self.enable_find_in_object_for_key:
                child = self.manager.find( name, self.request.headers.get( 'Content-Type', None ) )

            if isinstance( child, DAVFolder ):
                return child
            elif child is not None:
                return self.get_entity_representation( name, child, location=None,
                                                                    representation = format,
                                                                    is_webdav=is_webdav )

        self.no_such_path( )

    #
    # PUT
    #

    def apply_permissions(self, contact):
        pass

    def post_put_processing(self, contact):
        return True

    def do_PUT(self, name):

        payload = self.request.get_request_payload( )

        contact = self.manager.find( name=name,
                                     content_type=self.request.headers.get( 'Content-Type', None ) )

        if not contact:
            # Create
            contact = self.manager.create( name=name,
                                           payload=payload,
                                           if_match = self.request.headers.get('If-Match', None),
                                           content_type=self.request.headers.get( 'Content-Type', None ) )
            self.apply_permissions( contact )
            result_status = 201
        else:
            # Update
            result_status = 204
            contact = self.manager.update( name=name,
                                           payload=payload,
                                           content_type=self.request.headers.get( 'Content-Type', None ),
                                           if_match = self.request.headers.get('If-Match', None),
                                           entity=contact )

        self.post_put_processing( contact )

        self.context.commit( )

        headers = { 'Etag':     u'{0}:{1}'.format(contact.object_id, contact.version), }

        if self.context.user_agent_description[ 'webdav' ][ 'supportsLocation' ]:
            headers[ 'Location' ] = '/dav/Contacts/{0}'.format( contact.get_file_name( ) )

        self.request.simple_response( result_status,
                                      data=None,
                                      mimetype=u'text/x-vcard; charset=utf-8',
                                      headers=headers )

    #
    # DELETE
    #

    def pre_delete_processing(self, contact):
        return True

    def post_delete_processing(self, contact):
        return True

    def do_DELETE(self, name):

        contact = self.manager.find( name, content_type=None )

        if not contact:
            self.no_such_path()

        if self.pre_delete_processing( contact ):
            # Delete the contact
            if contact.is_account:
                self.simple_response( 423, message='Account objects cannot be deleted.' )
                return

            self.manager.delete( contact )
            self.post_delete_processing( contact )

        self.context.commit( )
        self.request.simple_response( 204 )

    #
    # REPORT
    #

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
        elif parser.report_name == 'addressbook-multiget':
            resources = [ ]
            self.log.info( 'Found {0} references in multiget'.format( len( parser.references ) ) )
            for href in parser.references:
                try:
                    key = href.split( '/' )[ -1 ]
                    resources.append( self.get_object_for_key( key ) )
                except NoSuchPathException, e:
                    self.log.debug( 'Missing resource {0} in collection'.format( key ) )
                except Exception, e:
                    self.log.exception( e )
                    raise e
            stream = StringIO( )
            properties, namespaces = parser.properties
            Multistatus_Response( resources=resources,
                                  properties=properties,
                                  namespaces=namespaces,
                                  stream=stream)
            self.request.simple_response( 207,
                                          data=stream.getvalue(),
                                          mimetype=u'text/xml; charset=utf-8' )
        else:
            raise NotImplementedException('REPORT "{0}" not supported by ContactsFolder'.format( parser.report_name ) )

    #
    # OPTIONS
    #

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'OPTIONS',   'GET',       'HEAD',     'POST',      'PUT',  'DELETE',
                    'TRACE', 'COPY', 'MOVE',  'PROPFIND', 'PROPPATCH', 'LOCK', 'UNLOCK',
                    'REPORT', 'ACL',  ]
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=u'text/plain',
                                     headers={ 'DAV':           '1, 2, access-control',
                                               'Allow':         ','.join(methods),
                                               'Connection':    'close',
                                               'MS-Author-Via': 'DAV'} )
