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

MIMESTRING_TO_FORMAT = { 'text/calendar': 'ics',
                         'text/vcard':    'vcf',
                         'text/json':     'json',
                         'text/yaml':     'yaml',
                         'text/xml':      'xml',  }

def mimestring_to_format( mimestring, default_format='vcf' ):
    if mimestring:
        return MIMESTRING_TO_FORMAT.get( mimestring.lower( ), default_format )
    return default_format  

class DAVEntityManager(object):
    
    def __init__(self, context):
        self.context = context
        self.last_format = None
        
    @property
    def format(self):
        return self.last_format

    def convert_uid_to_object_id(self, uid):
        if not uid:
            return None
        if uid.isdigit( ):
            return int( uid )
        elif uid.endswith( '@{0}'.format( self.context.cluster_id ) ):
            return int( uid[ :-len('@{0}'.format( self.context.cluster_id ) ) ] )
        else:
            return None

    def inspect_name(self, name, default_format='ics'):
        uid = name
        extension = name.split('.')[-1:][0]
        if extension == name:
            extension = None
            format = default_format
        else:
            format = extension.lower()
            if format not in ( 'ics', 'vjl', 'json', 'vcf', 'xml', 'yaml' ):
                format = default_format
                uid = name
                object_id = None
            elif format in ( 'json', 'xml', 'yaml' ):
                uid = name[ : - ( len( format ) + 1 ) ]
            elif format in ( 'ics', 'vjl', 'vcf' ):
                uid = name[ :- ( len( format ) + 1 ) ]
                format = 'ics'
        object_id = self.convert_uid_to_object_id( uid )
        #self.log.debug( 'Format: {0} Extension: {1} UID: {2} ObjectId: {3}'.format( format, extension, uid, object_id ) )
        return ( format, extension, uid, object_id )

    def find(self, name, payload, content_type, encoding=None):
        raise NotImplementedException()
        
    def create(self, name, payload, content_type, encoding=None):
        raise NotImplementedException()
