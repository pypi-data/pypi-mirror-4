#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy       import *
from coils.core       import *
from coils.core.logic import GetCommand

class GetContacts(GetCommand):
    __domain__ = "enterprise"
    __operation__ = "get-contacts"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        self.kinds = None
        Command.parse_parameters(self, **params)
        if ('enterprise' in params):
            self.enterprises = [ params.get('enterprise') ]
            self.set_single_result_mode();
        elif ('enterprises' in params):
            self.enterprises = params.get('enterprises')
            self.set_multiple_result_mode();

    def run(self):
        db = self._ctx.db_session()
        self.disable_access_check()
        
        response = { }
        if self.enterprises:
            for enterprise in self.enterprises:
                response[enterprise.object_id] = [ ]
            query = db.query(CompanyAssignment).\
                        filter(CompanyAssignment.parent_id.in_([x.object_id for x in self.enterprises]))
            assignments = query.all()
            if assignments:               
                contacts = self._ctx.run_command('contact::get', ids=[ x.child_id for x in assignments ], contexts=self.context_ids)
                for assignment in assignments:
                    for contact in contacts:
                        if (assignment.child_id == contact.object_id):
                            response[assignment.parent_id].append(contact)

        # class response based on mode
        if response:
            if self.single_result_mode:
                self._result = response[self.enterprises[0].object_id]
            else:
                self._result =  response
            return
            
        # We have nothing to return, so just return an empty of the appropriate type
        if (self.single_result_mode):
            self._result = [ ]
        else:
            self._result =  { }
