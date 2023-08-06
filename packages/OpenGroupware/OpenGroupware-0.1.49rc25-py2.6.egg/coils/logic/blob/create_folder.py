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
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import CreateCommand
from command            import BLOBCommand
from keymap             import COILS_FOLDER_KEYMAP

class CreateFolder(CreateCommand, BLOBCommand):
    __domain__    = "folder"
    __operation__ = "new"

    def prepare(self, ctx, **params):
        self.keymap = COILS_FOLDER_KEYMAP
        self.entity = Folder
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        self._parent = params.get('folder', None)

    def run(self):
        #TODO: If a project_id is set verify that it is valid
        #TODO: If a company_id is set verify that it is valid
        #TODO: If a parent_id is set verify that it is value
        #TODO: Verify that some combination of project/company/parent is set
        CreateCommand.run(self)
        self.obj.owner_id = self._ctx.account_id
        self.obj.creator_id = self._ctx.account_id
        
        if not self._parent:
            # A parent was not specified via the parent attribute, so we try to 
            # marshal the parent specified via Omphalos unless the folder is a root
            # folder [has no parent]
            if self.obj.folder_id:
                self._parent = self._ctx.run_command('folder::get', id = self.obj.folder_id)
                if not self._parent:
                    raise CoilsException('Cannot marshal parent folderId#{0}'.format(self.object.folder_id))
        else:
            self.obj.folder_id = self._parent.object_id
                    
        if self._parent:
            # Inherit the project if from the parent
            self.obj.project_id = self._parent.project_id
            
        self.inherit_acls()            
            
        self.save()
        self._ctx.flush()
