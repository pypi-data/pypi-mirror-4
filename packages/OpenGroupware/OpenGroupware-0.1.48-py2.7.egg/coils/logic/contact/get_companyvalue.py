#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from command             import ContactCommand

class GetCompanyValue(Command, ContactCommand):
    __domain__ = "contact"
    __operation__ = "get-companyvalue"
    mode = None

    def __init__(self):
        self.access_check = True
        Command.__init__(self)
        
    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._contact = params.get('contact', None)        
        self._name = params.get('name', None)        

    def run(self):
        self.access_check = False
        db = self._ctx.db_session()
        query = db.query(CompanyValue).filter(and_(CompanyValue.parent_id == self._contact.object_id, CompanyValue.name==self._name))
        result = query.all()
        if result:
            self.set_return_value(result[0])
        else:
            self.set_return_value(None)
