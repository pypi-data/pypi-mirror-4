#
# Copyright (c) 2009, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy         import *
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetResource(GetCommand):
    __domain__ = "resource"
    __operation__ = "get"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if (('name' in params) or ('names' in params)):
            self.query_by = 'name'
            # Recall by name(s)
            if ('name' in params):
                # This is a request for a single object
                self.mode = 1
                self.names = [ params['name'] ]
            else:
                self.mode = 2
                self.names = params['names']
        elif ('appointment' in params):
            self.mode = 2
            self.query_by = 'appointment'
            self.appointment = params['appointment']
        elif ('email' in params):
            self.query_by = 'email'
            self.mode = 2
            self._email = params['email'].lower()

    def run(self):
        db = self._ctx.db_session()
        query = None
        self.log.debug('Query mode is {0}'.format(self.query_by))
        if (self.query_by == 'name'):
            if (len(self.names)):
                query = db.query(Resource).filter(and_(Resource.name.in_(self.names),
                                                           Resource.status != 'archived'))
            else:
                query = None
        elif (self.query_by == 'email'):
            query = db.query(Resource).filter(Resource.email.ilike(self._email))
        elif (self.query_by == 'appointment'):
            if (isinstance(self.appointment, Appointment)):
                x = self.appointment.get_resource_names()
                if (len(x) > 0):
                    query = db.query(Resource).filter(and_(Resource.name.in_(x),
                                                            Resource.status != 'archived'))
                else:
                     #Shortcut
                      self.set_return_value([])
                      return
            else:
                raise CoilsException('Provided entity is not an Appointment')
        elif (self.query_by == 'object_id'):
            query = db.query(Resource).filter(and_(Resource.object_id.in_(self.object_ids),
                                                       Resource.status != 'archived'))

        else:
            # Recall all
            self.mode = 2
            query = db.query(Resource).filter(Resource.status != 'archived')
        # Retrieve data
        if query is None:
            self.set_return_value([])
        else:
            self.set_return_value(query.all())
