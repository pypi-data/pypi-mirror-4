#
# Copyright (c) 2009, 2012
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
#
from sqlalchemy          import *
from coils.core          import *
from coils.foundation    import *
from coils.logic.address import GetCompany
from command             import ContactCommand

class GetContact(GetCompany, ContactCommand):
    __domain__ = "contact"
    __operation__ = "get"
    mode = None

    def __init__(self):
        self.access_check = True
        GetCompany.__init__(self)
        self._carddav_uid = None
        self._email = None

    def parse_parameters(self, **params):
        GetCompany.parse_parameters(self, **params)
        
        if 'uid' in params or 'href' in params:
            self._uid  = unicode( params.get( 'uid', None ) )
            self._href = unicode( params.get( 'href', None ) )
            if not self._href: self._href = self._uid
            if not self._uid:  self._uid = self._href
            self.set_single_result_mode( )
        else:
            self._uid = None
            
        if 'email' in params: 
            self._email = params.get('email').lower()
            self.set_multiple_result_mode( )
            
        self._archived = params.get('archived', False)
        
        if ('properties' in params):
            self._properties = params.get('properties')
        else:
            self._properties = [Contact]

    def run(self):
        db = self._ctx.db_session( )
        query = db.query( *self._properties ).with_labels( ) 
        
        if self._archived:
            query = query.filter( Contact.status != 'archived' )
            
        if self._uid:
            print self._uid, self._href
            _or = or_( Contact.href == self._href, Contact.uid == self._uid )
            if self.object_ids: 
                _or = _or( _or, Contact.object_id.in_( self.object_ids ) )
            query = query.filter( _or )
        elif self._email:
            # search by e-mail address
            
            query = query.join( CompanyValue ).\
                    filter( and_( CompanyValue.string_value.ilike( self._email ),
                                  CompanyValue.name.in_( [ 'email1', 'email2', 'email3' ] ) ) )
        else:
            # search by objectId(s)
            query = query.filter( Contact.object_id.in_( self.object_ids ) )
         
        result = query.all ( )
        print ('contact::get returning {0} contacts'.format( len(result) ) )
        self.set_return_value( result) 
