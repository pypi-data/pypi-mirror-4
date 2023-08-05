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
# THE SOFTWARE.
#
import uuid
from coils.core           import *
from coils.net            import PathObject

class EntityObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def do_PUT(self, name):
        # TODO: This method has become a bit of a monster;  break the mode=file
        #       operations out to their own method
        payload = self.request.get_request_payload()
        mimetype = self.request.headers.get('Content-Type', 'application/octet-stream')
        scratch_file = BLOBManager.ScratchFile()
        scratch_file.write(payload)
        scratch_file.seek(0)
        attachment = None
        
        # Detect the mode for the operation; we fall through to the
        # default but allow an alternate to be specified via the URL
        # parameter "mode".  Currently mode "file" is supported to
        # easily allow the content of documents [files in projects] to
        # be updated and for documents [files in projects] to be 
        # created.
        mode = None
        if 'mode' in self.parameters:
            mode = self.parameters['mode'][0].lower()
        else:
            mode = 'default'

        if mode == 'file':
            #
            # Special handling for creating or updating document content via AttachFS
            #
            document  = None
            if isinstance(self.entity, Folder):
                # Determine the target filename.  If none is specified 
                # then we make one up; essentially a UUID/GUID with a 
                # ".bin" extension.  Although sending file create request
                # without a filename seems stupid.
                if name:
                    # BUG: names without extenstions may not work!
                    document = self.context.run_command('folder::ls', id=self.entity.object_id, name=name)
                    if document:
                        document = document[0]
                else:
                    # BUG: Just due to URL parsing semantics I belive this code path
                    #      is unreachable.  If no target name is provided it just seems
                    #      to fall through to attachment mode.
                    name = '{0}.bin'.format(uuid.uuid4().hex)
            elif isinstance(self.entity, Document):
                # We already know the file, so we don't need a filename
                # Posting content to a File via AttachFS *always*
                # updates the contents of said file - potentially
                # creating a new version depending on the storage
                # backend
                document = self.entity
            else:
                raise CoilsException('Mode "file" not support by AttachFS for entities of type "{0}"'.format(self.entity))
                
            if not document:
                # CREATE DOCUMENT / FILE
                # A matching document was not found, we are going to create a document
                document = self.context.run_command('document::new', name    = name,
                                                                  values  = { },
                                                                  folder  = self.entity,
                                                                  handle  = scratch_file)   
            else:
                # UPDATE DOCUMENT / FILE (possibly rename)
                # A document was found [or specified as the target] so we are doing an update
                self.context.run_command('document::set', object = document,
                                                          name = name,
                                                          values = {  },
                                                          handle = scratch_file)

            # For best WebDAV compatibility set the expected properties on the document
            self.context.property_manager.set_property(document,
                                                       'http://www.opengroupware.us/mswebdav',
                                                       'isTransient',
                                                       'NO')
            self.context.property_manager.set_property(document,
                                                       'http://www.opengroupware.us/mswebdav',
                                                       'contentType',
                                                       mimetype)
                                                       
            # Respond to client
            self.context.commit()
            self.request.simple_response(201,
                                         mimetype=mimetype,
                                         headers= { 'Content-Length': str(document.file_size),
                                                    'X-OpenGroupware-Document-Id': str(document.object_id),
                                                    'X-OpenGroupware-Folder-Id': str(document.folder_id),
                                                    'Etag': '{0}:{1}'.format(document.object_id, document.version),
                                                    'Content-Type': document.mimetype } )
                
        elif mode == 'default':
            #
            # Default AttachFS behavior
            #   
            attachment = self.context.run_command('attachment::new', handle=scratch_file,
                                                                    name=name,
                                                                    entity=self.entity,
                                                                    mimetype=mimetype)
            self.context.commit()
        
            if (attachment is not None):
                self.request.simple_response(201,
                                            mimetype=mimetype,
                                            headers= { 'Content-Length': str(attachment.size),
                                                        'Etag': attachment.uuid,
                                                        'Content-Type': attachment.mimetype } )
            else:
                # TODO; Can this happen without an exception having occurred?
                raise CoilsExcpetion('Ooops!')
        else:
            raise CoilsException('Unrecognized mode "{0}" specified for AttachFS operation.'.format(mode))
