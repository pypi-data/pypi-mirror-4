#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core         import *
from coils.core.logic   import DeleteCommand
from command            import ProjectCommand

class DeleteProject(DeleteCommand, ProjectCommand):
    __domain__    = "project"
    __operation__ = "delete"

    def prepare(self, ctx, **params):
        DeleteCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        DeleteCommand.parse_parameters(self, **params)

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('project::get', id=object_id,
                                                     access_check=access_check)

    def run(self):
        
        # Check rights
        if self._ctx.is_admin:
            pass
        else:
            rights = self._ctx.access_manager.access_rights(self.obj, contexts=self.context_ids)
            if not (('d' in rights) or ('a' in rights)):
                raise AccessForbiddenException('Insufficient privileges to delete {0}'.format(self.obj))        
        
        # Delete Note relations
        notes = self._ctx.run_command('project::get-notes', project=self.obj)
        for note in notes:
            note.project_id = None
            #TODO: Check if the note is still associated with anything
            
        # Delete assignements
        self.purge_assignments()        
        
        # Delete folder
        folder = self._ctx.run_command('project::get-root-folder', project=self.obj)
        if folder:
            self._ctx.run_command('folder::delete', object=folder)
            
        DeleteCommand.run(self)
        self.notify()
