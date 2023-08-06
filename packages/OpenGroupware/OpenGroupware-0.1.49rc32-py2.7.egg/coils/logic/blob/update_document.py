#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import UpdateCommand
from keymap             import COILS_DOCUMENT_KEYMAP
from command            import BLOBCommand

class UpdateDocument(UpdateCommand, BLOBCommand):
    __domain__    = "document"
    __operation__ = "set"

    def prepare(self, ctx, **params):
        self.keymap = COILS_DOCUMENT_KEYMAP
        self.entity = Document
        UpdateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        UpdateCommand.parse_parameters(self, **params)
        self._folder      = params.get('folder', None)
        self._project     = params.get('project', None)
        self._appointment = params.get('appointment', None)
        self._company     = params.get('contact', params.get('enterprise', None))
        self._name        = params.get('name', None)
        self._annotation  = params.get('annotation', None)
        self._input       = params.get('handle', None)

    def run(self):
        UpdateCommand.run(self)
        if (self._name is not None):
            self.obj.extension    = self._name.split('.')[-1]
            self.obj.name         = '.'.join(self._name.split('.')[:-1])
        self.obj.modified = self._ctx.get_utctime()
        self.obj.status       = 'updated'
        self.set_context(self.obj, folder=self._folder,
                                   project=self._project,
                                   company=self._company,
                                   appointment=self._appointment)
        if self._input:
            self.obj.version_count += 1
            manager = self.get_manager(self.obj)
            self.store_to_version(manager, self.obj, self._input)
            self.store_to_self(manager, self.obj, self._input)
        self.set_result(self.obj)
