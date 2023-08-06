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
from sqlalchemy import *
from coils.core import *
from coils.core.logic import GetCommand

class GetNotes(GetCommand):
    __domain__ = "object"
    __operation__ = "get-notes"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._context = params.get('context', None)
        if (self._context is None):
            raise CoilsException('No object specified for contextual note retrieval')

    def add_comments(self, notes):
        # TODO: Can we get all the handles at once?
        self.log.info('getting comments')
        for note in notes:
            handle = self._ctx.run_command('note::get-handle', id=note.object_id)
            # TODO: Do a nicer block read
            note.content = handle.read()
        return notes

    def run(self):
        self.set_multiple_result_mode()
        query = None
        if (self._context is not None):
            if (isinstance(self._context, Appointment)):
                query = self._ctx.db_session().query(Note).filter(Note.appointment_id == self._context.object_id)
            elif (isinstance(self._context, Project)):
                query = self._ctx.db_session().query(Note).filter(Note.project_id == self._context.object_id)
            elif (isinstance(self._context, Contact)):
                query = self._ctx.db_session().query(Note).filter(Note.company_id == self._context.object_id)
            elif (isinstance(self._context, Enterprise)):
                query = self._ctx.db_session().query(Note).filter(Note.company_id == self._context.object_id)
        if query:
            self.set_return_value(self.add_comments(query.all()))
        else:
            self.set_return_value([])
