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
from contactfolder                    import ContactFolder


class PersonalContactsFolder(ContactFolder):
    
    def __init__(self, parent, name, **params):
        ContactFolder.__init__( self, parent, name, **params )
        self.enable_find_in_object_for_key = False

    def _load_contents(self):
        #
        # TODO: Implement
        #
        self.empty_content( )
        return True

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

    def get_ctag(self):
        return self.get_ctag_for_entity('Person')

    #
    # PUT
    #

    def apply_permissions(self, contact):
        if contact.owner_id == self.contact.account_id:
            contact.is_private = 1        
        pass
        
    def post_put_processing(self, contact):
        return True

    #
    # DELETE
    #

    def pre_delete_processing(self, contact):
        return True

    def post_delete_processing(self, contact):
        return True        

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
