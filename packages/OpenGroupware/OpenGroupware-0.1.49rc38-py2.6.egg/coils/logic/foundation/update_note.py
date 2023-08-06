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
from datetime           import datetime
from coils.core         import *
from coils.core.logic   import UpdateCommand
from keymap             import COILS_NOTE_KEYMAP

class UpdateNote(UpdateCommand):
    __domain__    = "note"
    __operation__ = "set"

    def prepare(self, ctx, **params):
        self.keymap = COILS_NOTE_KEYMAP
        self.entity = Note
        UpdateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        UpdateCommand.parse_parameters(self, **params)
        if ('text' in params): self.values['text'] = params['text']
        self._context = params.get('context', None)

    def run(self):


        UpdateCommand.run(self)

        self.obj.modified = self._ctx.get_utctime()

        if 'content' in self.values:
            self.obj.content = self.values.get('content')

        # Should a note be allowed to be orphaned?  That is, be
        # left with no context(s) at all?  [ related to no Appointment,
        # Project, or Contact/Enterprise ].  If that occurs should an
        # exception be raised or at least generate a low-level
        # AdministrativeNotice?

        if (self._context is not None):

            if (isinstance(self._context, Appointment)):
                # Context is an Appointment, assign to appointment_id
                self.obj.appointment_id = self._context.object_id

            elif (isinstance(self._context, Project)):
                # Context is an Project, assign to project_id
                self.obj.project_id = self._context.object_id

            elif (isinstance(self._context, Contact)):
                # Context is an Contact, assign to company_id
                self.obj.company_id = self._context.object_id

            elif (isinstance(self._context, Enterprise)):
                # Context is an Enterprise, assign to company_id
                self.obj.company_id = self._context.object_id

        handle = BLOBManager.Create(self.obj.get_path())
        handle.write(self.obj.content)
        self.obj.file_size = handle.tell()
        BLOBManager.Close(handle)
