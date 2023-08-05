#
# Copyright (c) 2011, 2012 
#  Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.foundation    import *
from coils.core.logic    import DeleteCommand
from command             import BLOBCommand

class DeleteDocument(DeleteCommand, BLOBCommand):
    __domain__ = "document"
    __operation__ = "delete"

    def __init__(self):
        DeleteCommand.__init__(self)
        self._common_init()

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('document::get', id=object_id,
                                                      access_check=access_check)

    def run(self):
        
        # Check rights
        if self.access_check:
            if self._ctx.is_admin:
                pass
            else:
                rights = self._ctx.access_manager.access_rights(self.obj, contexts=self.context_ids)
                if self.debug: self.log.debug('Rights found for documentId#{0} entity: {1}'.format(self.obj.object_id, rights))
                if 'd' not in rights:
                    raise AccessForbiddenException('Insufficient privileges to delete documentId#{0}'.format(self.obj.object_id))
                    
        self.set_result(False)
        
        manager = self.get_manager(self.obj)
        document_path = manager.get_path(self.obj)
        versions = self._ctx.run_command('document::get-versions', document=self.obj)
        paths = [ document_path ]
        for version in range(0, self.obj.version_count + 1):
            version_path = manager.get_path(self.obj, version=version)
            if version_path:
                paths.append(version_path)
        for path in paths:
            # TODO: Deletes are probably worth logging
            if self.debug:
                self.log.debug('Deleting document path "{0}".'.format(path))
            BLOBManager.Delete(path)
        if self.debug: self.log.debug('Deleting database entities for documentId#{0}'.format(self.obj.object_id))
        DeleteCommand.run(self)
        self.set_result(True)
