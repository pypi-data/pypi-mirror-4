#
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
#
from sqlalchemy          import *
from coils.core          import *

class DeleteCollectionAssignment(Command):
    # TODO: Delete related collection assignments
    __domain__    = "collection"
    __operation__ = "delete-assignment"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.collection       = params.get('collection',None)
        if ('entity' in params):
            self.assigned_id      = params.get('entity').object_id
        elif ('assigned_id' in params):
            self.assigned_id      = int(params.get('assigned_id'))
        else:
            raise CoilException('Assignment to delete not specified as entity or assigned_id')

    def run(self):
        self.collection.version += 1
        self._ctx.db_session().\
                query(CollectionAssignment).\
                filter(and_(CollectionAssignment.collection_id == self.collection.object_id,
                            CollectionAssignment.assigned_id   == self.assigned_id)).\
                delete(synchronize_session='fetch')
        self.set_return_value(True)