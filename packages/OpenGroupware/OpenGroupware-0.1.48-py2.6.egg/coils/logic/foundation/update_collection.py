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
from coils.core          import *
from coils.core.logic    import UpdateCommand
from keymap              import COILS_COLLECTION_KEYMAP

from command import CollectionAssignmentFlyWeight

class UpdateCollection(UpdateCommand):
    __domain__ = "collection"
    __operation__ = "set"

    def __init__(self):
        UpdateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap =  COILS_COLLECTION_KEYMAP
        self.entity = Collection
        UpdateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        UpdateCommand.parse_parameters(self, **params)

    def _form_assignments(self, assignments):
        if (isinstance(assignments, list)):
            return [ CollectionAssignmentFlyWeight(assignment, ctx=self._ctx)
                     for assignment in assignments ]
        else:
            raise CoilsException('Provided membership must be a list')

    def do_assignments(self):
        membership = KVC.subvalues_for_key(self.values, ['_MEMBERSHIP', 'membership'])
        assignments = self._form_assignments(membership)
        if (len(assignments) > 0):
            self._ctx.run_command('collection::set-assignments', update=assignments,
                                                                 collection=self.obj)

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('collection::get', id=object_id,
                                                         access_check=access_check)

    def run(self):
        UpdateCommand.run(self)
        self.do_assignments()
