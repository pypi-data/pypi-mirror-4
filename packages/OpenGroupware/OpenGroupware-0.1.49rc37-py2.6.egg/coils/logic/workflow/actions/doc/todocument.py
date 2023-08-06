#
# Copyright (c) 2012, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
import zipfile, shutil
from tempfile            import NamedTemporaryFile
from coils.core          import *
from coils.core.logic    import ActionCommand

class MessageToDocumentAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "message-to-document"
    __aliases__   = [ 'messageToDocument', 'messageToDocumentAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):

        if self._project_id.isdigit():
            project = self._ctx.run_command( 'project::get', id=long( self._project_id ) )
        else:
            project = self._ctx.run_command( 'project::get', number=self._project_id )

        if not project:
            raise CoilsException( 'Unable to marshall project identified as "{0}"'.format( self._project_id ) )

        folder = self._ctx.run_command( 'project::get-path', path=self._filepath, project=project, create=True )

        document = self._ctx.run_command( 'folder::ls', id=folder.object_id, name=self._filename )
        if document:
            # A document at this path already exists, so we are updating it
            # This will create a new revision of the document, provided the storage backend
            # supports document versioning
            document = document[ 0 ]
            self._ctx.run_command( 'document::set', object=document, values = {  }, handle = self.rfile )
        else:
            document = self._ctx.run_command( 'document::new', name = self._filename,
                                                               values  = { },
                                                               project = project,
                                                               folder  = folder,
                                                               handle  = self.rfile )
        # Update the abstract of the document
        document.abstract = self._abstract

        # Store the MIME-Type of the content as a property on the document [ticket:#110]
        self._ctx.property_manager.set_property( document,
                                                 'http://www.opengroupware.us/mswebdav',
                                                 'contentType',
                                                 self.input_message.mimetype )
        self._ctx.property_manager.set_property( document,
                                                 'http://www.opengroupware.us/mswebdav',
                                                 'isTransient',
                                                 'NO' )

        self.wfile.write( unicode( document.object_id ) )

    def parse_action_parameters(self):

        self._project_id = self.action_parameters.get( 'projectId', None )
        if not self._project_id:
            raise CoilsException( 'No project specified for document save' )
        self._project_id = self.process_label_substitutions( self._project_id )

        self._filepath = self.action_parameters.get( 'filePath', '/' )
        self._filepath = self.process_label_substitutions( self._filepath )

        self._filename = self.action_parameters.get( 'filename', 'noname.data' )
        self._filename = self.process_label_substitutions( self._filename )

        self._abstract = self.action_parameters.get( 'abstract', self._filename )
        self._abstract = self.process_label_substitutions( self._abstract )

    def do_epilogue(self):
        pass
