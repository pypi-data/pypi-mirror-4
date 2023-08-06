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

from coils.core import NotImplementedException
from coils.core.vcard                  import Parser as VCard_Parser
from coils.core.vcard                  import NoContentInVCardData
from entitymanager import DAVEntityManager, mimestring_to_format

class DAVContactManager(DAVEntityManager):
    '''
    Entity manager for Contact operations.
    '''

    def __init__(self, context):
        DAVEntityManager.__init__(self, context)

    def find(self, name, content_type, encoding=None):
        print '--FIND--'
        format = mimestring_to_format( content_type )
        format, extension, uid, object_id = self.inspect_name( name, default_format = format)
        if object_id:
            contact = self.context.run_command( 'contact::get', id=object_id )
        else:
            contact = self.context.run_command( 'contact::get', uid=uid, href=name)
        self.last_format = format
        print 'CONTACT: {0}'.format( contact )
        return contact

    def create(self, name, payload, content_type, encoding=None, if_match=None):
        format = mimestring_to_format( content_type, default_format = 'vcf' )
        self.last_format = format
        if format == 'vcf':
            payload = VCard_Parser.Parse( payload, self.context )
            if len( payload ) == 0:
                raise NoContentInVCardData( )
            elif len( payload ) == 1:
                payload = payload[ 0 ]
            else:
                raise NotImplementedException( 'Multiple contact PUT not implemented ' )
        else:
            raise NotImplementedException( 'PUT (create) of object format "{0}" not implemented'.format( format ) )
        contact = self.context.run_command( 'contact::new', values=payload )
        contact.href = name
        return contact

    def update(self, name, entity, content_type, payload, encoding=None, if_match=None):
        format = mimestring_to_format( content_type, default_format = 'vcf' )
        self.last_format = format
        if format == 'vcf':
            payload = VCard_Parser.Parse( payload, self.context )
            if len( payload ) == 0:
                raise NoContentInVCardData( )
            elif len( payload ) == 1:
                payload = payload[ 0 ]
            else:
                raise NotImplementedException( 'Multiple contact PUT not implemented ')
        else:
            raise NotImplementedException( 'PUT (update) of object format "{0}" not implemented'.format( format ) )
        return self.context.run_command( 'contact::set', object=entity, values=payload )

    def delete(self, entity):
        return self.context.run_command( 'contact::delete', object=entity )

