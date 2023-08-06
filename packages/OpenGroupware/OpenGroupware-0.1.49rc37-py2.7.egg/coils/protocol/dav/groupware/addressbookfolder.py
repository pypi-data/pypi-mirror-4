#
# Copyright (c) 2012
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
from coils.protocol.dav.managers       import DAVContactManager, mimestring_to_format
from contactfolder                     import ContactFolder


class AddressBookFolder(ContactFolder):
    def __init__(self, parent, name, **params):
        ContactFolder.__init__( self, parent, name, **params )
        self.enable_find_in_object_for_key = False

    def __repr__(self):
        return '<AddresBookFolder name="{0}"/>'.format( self.name )

    # PROP: RESOURSETYPE
    def get_property_webdav_resourcetype(self):
        '''See RFC2518, Section 13.9'''
        return u'<D:collection/><E:addressbook/>'

    def get_property_carddav_supported_address_data(self):
         return u'<E:address-data-type content-type="text/vcard" version="3.0"/>'

    def get_ctag(self):
        return self.get_ctag_for_collection()

    def _load_contents(self):
        content =  self.context.run_command('collection::get-assignments', collection=self.entity,
                                                                           as_entity=True)
        if (len(content) > 0):
            for entity in content:
                if ( ( entity.object_id > 10000 ) and ( isinstance( entity, Contact ) ) ):
                    self.insert_child( entity.object_id, entity, alias=entity.get_file_name( ) )
        else:
            self.empty_content()

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
            # TODO: Perhaps this can be done much more efficiently
            self.load_contents( )
            child = self.get_child( name )            
            if child:
                return self.get_entity_representation( name, child, location=None,
                                                                    representation = 'ics',
                                                                    is_webdav=is_webdav )
        self.no_such_path( )

    #
    # PUT
    #

    def post_put_processing(self, contact):
        self.context.run_command( 'object::assign-to-collection', collection=self.entity, entity=contact )
        return True

    #
    #
    #

    def pre_delete_processing(self, contact):
        self.context.run_command( 'collection::delete-assignment', collection=self.entity, entity=contact )
        return False

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
                                     headers={ 'DAV':           '1, 2, access-control, addressbook',
                                               'Allow':         ','.join(methods),
                                               'Connection':    'close',
                                               'MS-Author-Via': 'DAV'} )
