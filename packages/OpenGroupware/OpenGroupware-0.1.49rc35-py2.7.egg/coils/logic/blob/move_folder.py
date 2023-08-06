#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from command             import BLOBCommand

class MoveFolder(SetCommand, BLOBCommand):
    __domain__ = "folder"
    __operation__ = "move"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        SetCommand.parse_parameters(self, **params)
        self.obj = params.get('folder', None)
        self.filename = params.get('to_filename', None)
        self.to_folder = params.get('to_folder', None)

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('folder::get', id=object_id,
                                                      access_check=access_check)

    def run(self):
        
        if self.access_check:
            rights = self._ctx.access_manager.access_rights(self.obj, contexts=self.context_ids)
            print 'RIGHTS: {0}'.format(rights)
            if self.debug:
                self.log.debug('Rights found for documentId#{0} entity: {1}'.format(self.obj.object_id, rights))
            if 'w' not in rights:
                raise AccessForbiddenException('Insufficient privileges to modify documentId#{0}'.format(self.obj.object_id))
                                    
        # TODO: Should the version of the document be bumped, although it's *contents*
        #       were not modified?  To bump the version of a document entity we would
        #       need to create a new version of the content - which means that a MOVE
        #       operation will be expensive.
        if self.to_folder:
            self.to_folder.modified = self._ctx.get_utctime()
            self.to_folder.status   = 'updated'
            
            if self.obj.folder_id != self.to_folder.object_id:
                if self.obj.project_id != self.to_folder.project_id:
                    # TODO: Can documents be *MOVED* between projects? At this point NO
                    #   Projects may have radically different backends and historical
                    #   document versions will still need to be 'findable'. Between
                    #   projects should be a copy or at worse a copy-and-delete-source.
                    # WARN: For now we are refusing this action!
                    raise NotImplementedException('Folders cannot be moved between projects')
                        # TODO: Check permissions!
                if self.access_check:
                    rights = self._ctx.access_manager.access_rights(self.to_folder, contexts=self.context_ids)
                    if self.debug:
                        self.log.debug('Rights found for folderId#{0} entity: {1}'.format(self.to_folder.object_id, rights))
                    if 'w' not in rights:
                        raise AccessForbiddenException('Insufficient privileges to place documentId#{0} into folderId#{1}'.\
                            format(self.obj.object_id, self.to_folder.object_id))
                self.obj.folder_id   = self.to_folder.object_id
            
                if self.to_folder.version:
                    self.to_folder.version  += 1 # Bump the folder's object version
                else:
                    self.to_folder.version = 2
                    
        if self.filename:
            # Filename as well as location has changed
            self.obj.name = self.filename

        self.increment_version()

        # TODO: Log the changes to file / folder in the audit log

        self.set_result(self.obj)

