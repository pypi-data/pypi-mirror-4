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
from coils.core                       import Contact
from contactfolder                    import ContactFolder


class AllContactsFolder(ContactFolder):
    
    def __init__(self, parent, name, **params):
        ContactFolder.__init__( self, parent, name, **params )

    def _load_contents(self):
        content = self.context.run_command('contact::list', properties = [ Contact ])
        if (len(content) > 0):
            for contact in content:
                self.insert_child( contact.object_id, contact, alias=contact.get_file_name( ) )
        else:
            self.empty_content()
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
        # TODO: Apply default permissions
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
