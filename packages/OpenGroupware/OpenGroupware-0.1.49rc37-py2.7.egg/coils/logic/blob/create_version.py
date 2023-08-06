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
import shutil
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import CreateCommand
from command            import BLOBCommand

class CreateVersion(CreateCommand, BLOBCommand):
    __domain__    = "document"
    __operation__ = "new-version"

    def prepare(self, ctx, **params):
        self.keymap = { }
        self.entity = DocumentVersion
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('document' in params):
            self._document = params.get('document')
        else:
            raise CoilsException('Request to create a version with no document.')
        self._rfile  = params.get('handle', None)

    def run(self):
        if (self._document.project_id is not None):
            # Project document
            self._document.version_count += 1
            # Document need to be persisted prior to storage
            self.save()
            manager = self.get_manager(self._document)
            self.store_to_version(manager, self._document, self._rfile)
            self.store_to_self(manager, self._document, self._rfile)
        else:
            raise NotImplementedException('Non-project documents not yet supported')
        self._result = self.obj
        # TODO: file_size
        # TODO: is_note
        # TODO: is_object_link
        # TODO: is_index_doc
        # TODO: db_status

