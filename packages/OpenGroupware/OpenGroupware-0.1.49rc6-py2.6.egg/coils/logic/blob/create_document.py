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
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import CreateCommand
from command            import BLOBCommand
from keymap             import COILS_DOCUMENT_KEYMAP

class CreateDocument(CreateCommand, BLOBCommand):
    __domain__    = "document"
    __operation__ = "new"

    def prepare(self, ctx, **params):
        self.keymap = COILS_DOCUMENT_KEYMAP
        self.entity = Document
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        self._folder      = params.get('folder', None)
        self._project     = params.get('project', None)
        self._appointment = params.get('appointment', None)
        self._company     = params.get('contact', params.get('enterprise', None))
        self._name        = params.get('name', None)
        self._annotation  = params.get('annotation', None)
        self._input       = params.get('handle', BLOBManager.ScratchFile())

    def run(self):
        CreateCommand.run(self)
        #
        # Take file extension from name if the name has more than one component, otherwise
        # the extension is none - and we just assume this is application/octet-stream, at
        # least for now.
        #
        parts = self._name.split('.')
        if (len(parts) > 1):
            self.obj.extension    = self._name.split('.')[-1]
            self.obj.name         = '.'.join(self._name.split('.')[:-1])
        else:
            self.obj.extension = None
            self.obj.name = self._name
        self.obj.creator_id   = self._ctx.account_id
        self.obj.created      = datetime.now()
        self.obj.modified     = self.obj.created
        self.obj.status       = 'inserted'
        self.obj.version_count = 1
        if ((self._project is None) and (self._folder is not None)):
            # If no project was specified but a folder was then we try to assume the
            # project assignment of the folder (if the folder is so assigned)
            if (self._folder.project_id is not None):
                self._project = self._ctx.run_command('project::get', id=self._folder.project_id)
                if (self._project is None):
                    self.log.error('Unable to marshall projectId#{0} related to specified folderId#{1}'.\
                                    format(self._folder.project_id,
                                           self._folder.object_id))
        if (self.obj.abstract is None):
            self.obj.abstract = self._name
        self.set_context(self.obj, folder=self._folder,
                                   project=self._project,
                                   company=self._company,
                                   appointment=self._appointment)
        self.inherit_acls()
                                   
        # The document entity needs to be persisted prior to remainder of this command
        self.save()
        
        # Store the content to the BLOB
        manager = self.get_manager(self.obj)
        self.store_to_version(manager, self.obj, self._input)
        self.store_to_self(manager, self.obj, self._input)
        
        # DONE
        self.set_result(self.obj)
