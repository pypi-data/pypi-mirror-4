# Copyright (c) 2009, 2010, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from StringIO                          import StringIO
from datetime                          import datetime
# DAV Classses
from coils.core                        import NotImplementedException, \
                                              NoSuchPathException
from coils.net                         import DAVObject, \
                                              DAVFolder, \
                                              Parser, \
                                              Multistatus_Response
from coils.core.vcard                  import Parser as VCard_Parser
from groupwarefolder                   import GroupwareFolder


class AccountsFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def is_collection_folder(self):
        return True

    # PROP: GETCTAG

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    # PROP: RESOURSETYPE
    def get_property_webdav_resourcetype(self):
        '''
        Return the resource type of the collection, which is always
        'collection'. See RFC2518, Section 13.9
        '''
        return u'<D:collection/><E:addressbook/>'

    def get_ctag(self):
        return self.get_ctag_for_collection()

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, COPY, MOVE',
                    'PROPFIND, PROPPATCH, LOCK, UNLOCK, REPORT, ACL' ]
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=u'text/plain',
                                     headers={ 'DAV':           '1, 2, access-control, addressbook',
                                               'Allow':         ','.join(methods),
                                               'Connection':    'close',
                                               'MS-Author-Via': 'DAV'} )

    # CONTENTS (Implementation)

    def _load_contents(self):
        accounts = self.context.run_command( 'account::get-all', access_check=False )
        for account in accounts:
            self.insert_child( account.object_id, account, alias=account.get_file_name( ) )
        return True

    def object_for_key( self, name, auto_load_enabled=True, is_webdav=False ):
        if name.startswith( '.' ):
            function_name = 'render_key_{0}'.format( name[ 1: ].lower().replace( '.', '_' ) )
            if hasattr( self, function_name ):
                return getattr( self, function_name )( name, is_webdav=is_webdav, auto_load_enabled=auto_load_enabled )
            else:
                self.no_such_path( )
        else:
            format, extension, uid, object_id = self.inspect_name( name, default_format = 'ics' )
            contact = None
            if self.is_loaded:
                contact = self.get_child( name )
                if not contact:
                    contact = self.context.run_command( 'contact::get', uid=uid )
            if not contact and object_id:
                contact = self.context.run_command( 'contact::get', id=object_id)
            if contact:
                return self.get_entity_representation( name, contact, location=None,
                                                                      representation = format,
                                                                      is_webdav=is_webdav )
        self.no_such_path( )

    #
    # REPORT
    #

    def do_REPORT(self):
        ''' Preocess a report request '''
        payload = self.request.get_request_payload( )
        self.log.debug( 'REPORT REQUEST: {0}'.format( payload ) )
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
            raise NotImplementedException('REPORT "{0}" not supported by AccountsFolder'.format( parser.report_name ) )
