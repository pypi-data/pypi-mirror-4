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
from command            import BLOBCommand

class DeleteFolder(DeleteCommand, BLOBCommand):
    __domain__    = "folder"
    __operation__ = "delete"

    def prepare(self, ctx, **params):
        DeleteCommand.prepare(self, ctx, **params)

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('folder::get', id=object_id,
                                                     access_check=access_check)
 
    def run(self):
        db = self._ctx.db_session()
        
        # Check rights
        if self._ctx.is_admin:
            pass
        else:
            rights = self._ctx.access_manager.access_rights(self.obj, contexts=self.context_ids)
            if not (('d' in rights) or ('a' in rights)):
                raise AccessForbiddenException('Insufficient privileges to delete {0}'.format(self.obj))
        
        # Delete Child Documents [this includes archived objects]
        query = db.query(Document).filter(Document.folder_id == self.obj.object_id)
        for document in query.all():
            self._ctx.run_command('document::delete', object=document)            
        
        # Delete Child Folders [this includes archived objects
        query = db.query(Folder).filter(Folder.folder_id == self.obj.object_id)
        for folder in query.all():
            self._ctx.run_command('folder::delete', object=folder)
        
        DeleteCommand.run(self)
        self.notify()
