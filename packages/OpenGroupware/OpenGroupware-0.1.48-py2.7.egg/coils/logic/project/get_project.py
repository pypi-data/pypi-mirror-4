#!/usr/bin/python
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from coils.foundation   import Project, Appointment, Contact, Enterprise

class GetProject(GetCommand):
    __domain__ = "project"
    __operation__ = "get"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._number = None
        self._name   = None
        if ('number' in params):
            self._number = params.get('number')
        elif ('name' in params):
            self._name = params.get('name')

    def run(self, **params):
        db = self._ctx.db_session()
        if (self._number is None) and (self._name is None):
            query = db.query(Project).filter(and_(Project.object_id.in_(self.object_ids),
                                                   Project.status != 'archived'))
        elif (self._number is not None):
            self.set_single_result_mode()
            query = db.query(Project).filter(and_(Project.number == self._number,
                                                   Project.status != 'archived'))
        elif (self._name is not None):
            self.set_single_result_mode()
            query = db.query(Project).filter(and_(Project.name == self._name,
                                                   Project.status != 'archived'))
        else:
            raise CoilsException('No criteria provided to project::get')
        self.set_return_value(query.all())
