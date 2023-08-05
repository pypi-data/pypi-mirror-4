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
import hashlib
from sqlalchemy       import *
from coils.core       import DocumentVersion, CoilsException, ServerDefaultsManager, Document, Folder, ACL, ProjectAssignment
from coils.foundation import blob_manager_for_ds, BLOBManager

class BLOBCommand(object):

    def _common_init(self):
        sd = ServerDefaultsManager()
        self.debug = sd.bool_for_default('OGoDocumentManagementDebugEnabled')

    def get_manager(self, document):
        manager = None
        if document.__entityName__ == 'Note':
            pass
            #TODO: provide a blob manager for Notes rather than the hard coded hack
        elif (document.project_id is not None):
            #NOTE: Do not use Logic, because we do *NOT* want the access manager involved here
            #project = self._ctx.run_command('project::get', id = document.project_id)
            project = document.project
            if project:
                # We are assuming this is a project document, so open it using a project path
                manager = blob_manager_for_ds(project.sky_url, project_id=project.object_id)
            else:
                pass
        else:
            # Document is not attached to a project, assuming this document is an attachment
            manager = blob_manager_for_ds('attachment:')
        if not manager:
            # TODO: sends administrative notice about inability to find a manager (Issue#173)
            self.log.warn('Unable to marshall a BLOB manager for documentId#{0}'.format(document.object_id))
        return manager

    def get_handle(self, manager, mode, document, version=None, encoding='utf-8', create=False):
        path = manager.get_path(document, version=version)
        if (path is None):
            raise CoilsException('Unable to determine BLOB path for document revision objectId#{0} revision#{1}'.\
                    format(document.object_id, version))
        handle = BLOBManager.Open(path, mode, encoding=encoding, version=version, create=create)
        if (handle is None):
            raise CoilsException('Unable to open handle for document revision objectId#{0} revision#{1}'.\
                    format(document.object_id, version))
        return handle

    def write(self, in_handle, out_handle):
        in_handle.seek(0)
        m = hashlib.sha512()
        data = in_handle.read(4096)
        while data != '':
            m.update(data)
            out_handle.write(data)
            data = in_handle.read(4096)
        out_handle.flush()
        return (m.hexdigest(), in_handle.tell())

    def delete_version(self, manager, document, version=None):
        BLOBManager.Delete(manager.get_path(document, version=version))
        return True

    def set_context(self, document, folder=None, project=None, company=None, appointment=None):
        if (folder is not None):
            document.folder_id = folder.object_id
        if (project is not None):
            document.project_id = project.object_id
        if (company is not None):
            document.company_id = company.object_id
        if (appointment is not None):
            document.appointment_id = appointment.object_id
            
    def inherit_acls(self):
        
        # This is only effective for Documents/Files and Folders
        if not (isinstance(self.obj, Document) or isinstance(self.obj, Folder)):
            return

        # The client supplied ACLs; doing so negates ACL inheritance
        # This property is set by the base SetCommand if ACL declarations
        # were included in the update
        if self.acls_from_client_saved:
            return
        
        # Assume ACL inheritance is *NOT* enabled
        inherit_acls = False
        
        # Determine if ACL inheritance is enabled on the Project
        if not self.acls_from_client_saved:
            prop = self._ctx.property_manager.get_property(self.obj.project_id, '57c7fc84-3cea-417d-af54-b659eb87a046', 'inheritACLs')
            if prop:
                if prop.get_value() == 'YES':
                    inherit_acls = True
            
        # If we didn't find it to be enabled we can return now
        if not inherit_acls:
            return 
         
        # ACL inheritance is enabled!  So copy the rights from the project to the new entity
        acls = self._ctx.db_session().query(ProjectAssignment).filter(ProjectAssignment.parent_id == self.obj.project_id)
        if acls:
            for acl in acls:
                if acl.permissions:
                    tmp = ACL(self.obj.object_id, acl.context_id, permissions=acl.permissions)
                    self._ctx.db_session().add(tmp)
            

    def create_version(self, document, change_text=None, checksum=None):
        dv = DocumentVersion(document, change_text=change_text, checksum=checksum)
        #i = self._ctx.db_session().execute(Sequence('key_generator'))
        self._ctx.db_session().add(dv)
        self._ctx.db_session().flush()
        self._ctx.db_session().refresh(dv)
        self._ctx.db_session().refresh(document)
        return dv

    def store_to_version(self, manager, document, input_stream):
        version = self.create_version(document)
        # Copy the file into the target container (file)
        handle = self.get_handle(manager, 'w', document, version=version.version,
                                                         encoding='binary',
                                                         create=True)
        checksum, file_size = self.write(input_stream, handle)
        BLOBManager.Close(handle)
        # Set the file size & checksum of the Document Version entity
        version.set_checksum(checksum)
        version.set_file_size(file_size)        
        # Set file size & checksum of Document entity
        document.set_file_size(file_size)


    def store_to_self(self, manager, document, input_stream):
        # TODO: This is not transactional; Hmmm, how to make it transactional?
        #       Perhaps we could create this as an aliased file name and move
        #       the data once the transaction compeletes [pending till commit?]
        #       Use the session_id as a filename suffix?
        handle = self.get_handle(manager, 'w', document, version=None,
                                                         encoding='binary',
                                                         create=True)
        checksum, file_size = self.write(input_stream, handle)
        BLOBManager.Close(handle)
        # Set file size & checksum of Document entity
        document.set_file_size(file_size)

