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
from keymap           import COILS_COLLECTION_ASSIGNMENT_KEYMAP

class AssignObject(Command):
    __domain__ = "object"
    __operation__ = "assign-to-collection"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.collection  = params.get('collection', None)  ## The collection in question
        self.assigned    = params.get('entity',     None)  ## Add these entities

    def check_parameters(self):
        if (self.collection is None):
            raise CoilsException('No collection provided to set-assignment')

    def get_max_key(self):
        max_key = 0
        for assignment in self.collection.assignments:
            if (assignment.sort_key > max_key):
                max_key = assignment.sort_key
        return max_key

    def get_assignment(self):
        db = self._ctx.db_session()
        query = db.query(CollectionAssignment).filter(and_(CollectionAssignment.collection_id == self.collection.object_id,
                                                           CollectionAssignment.assigned_id == self.assigned.object_id))
        result = query.all()
        if result:
            return result[0]
        else:
            return None

    def run(self):
        db = self._ctx.db_session()
        self.check_parameters()
        # TODO: Check for write access!
        self.obj = self.get_assignment()
        if not self.obj:
            self.obj = CollectionAssignment()
            self.obj.collection_id = self.collection.object_id
            self.obj.assigned_id = self.assigned.object_id
            self.obj.sort_key = self.get_max_key()
            self._ctx.db_session().add(self.obj)
            # TODO: generate an audit message?
            self.collection.version += 1
        self.set_return_value(self.collection)
