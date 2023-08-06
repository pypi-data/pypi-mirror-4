#
# Copyright (c) 2013
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

class FolderToZIPFileAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "folder-to-zipfile"
    __aliases__   = [ 'folderToZipFile', 'folderToZipFileAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def decompose_project_path(self, path_string):
        project_label = path_string.split( ':' )[0]
        folder_path = path_string[ len(project_label) + 1 : ]
        if not folder_path:
            folder_path = '/'
        return project_label, folder_path

    def folder_from_project_path(self, project_label, folder_path):
        project, folder = None, None
        if project_label.isdigit( ):
            project = self._ctx.run_command( 'project::get', id=long( project_label ) )
        if not project:
            project = self._ctx.run_command( 'project::get', number=project_label )
        if not project:
            raise CoilsException( 'Unable to marshall a project for label "{0}"'.format( project_label ) )

        folder = self._ctx.run_command( 'project::get-path', path=folder_path, project=project, create=True )
        if not folder:
            raise CoilsException( 'Unable to marshall a folder for path "{0}"'.format( folder_path ) )

        return project, folder

    def do_action(self):

        project, folder = self.folder_from_project_path( self.project_label, self.folder_path )
        self.log_message( 'Retrieving documents from OGo#{0} [Folder] of OGo#{1} [Project]'.format( folder.object_id, project.object_id, ), category='debug' )

        # Create the ZipFile object on the actions' write file handle
        zfile = zipfile.ZipFile( self.wfile, 'a', compression=zipfile.ZIP_DEFLATED )

        #List the contents of the folder
        ls = self._ctx.r_c( 'folder::ls', folder=folder )

        if 'any' in self.mimetypes_to_include:
            self.log_message( 'MIMETypes includes "any", all documents will be included', category='debug' )
        else:
            self.log_message( 'The following document types will be included: {0}'.format( ','.join( self.mimetypes_to_include )  ),
                              category='debug' )

        included_documents = [ ]

        for document in [ x for x in ls if isinstance( x, Document) ]:
            self.log_message( 'Considering OGo#{0} [Document]'.format( document.object_id, ), category='debug' )
            include = False
            if 'any' in self.mimetypes_to_include:
                include = True
            else:
                mimetype = self._ctx.type_manager.get_mimetype( document )
                if mimetype in self.mimetypes_to_include:
                    include = True

            if include:
                rfile = self._ctx.run_command( 'document::get-handle', document=document )
                if rfile:
                    zfile.write( rfile.name, arcname=document.get_file_name( ) )
                    BLOBManager.Close( rfile )
                    self.log_message( 'OGo#{0} [Document] appended to ZIP file'.format( document.object_id ), category='debug' )
                    included_documents.append( document )
                else:
                    raise CoilsException( 'Unable to marshall a handle for OGo#{0} [Document]'.format( document.object_id ) )

        # Add the content from the message handle
        zfile.close( )

        if self.purge_included_documents:
            for document in included_documents:
                self.log_message( 'Deleting included OGo#{0} [Document]'.format( document.object_id ), category='debug' )
                self._ctx.run_command( 'document::delete', object=document )

    def parse_action_parameters(self):

        project_path = self.action_parameters.get( 'projectPath', '' )
        if not project_path:
            raise CoilsException( 'No projectPath specified in folderToZipFile' )
        project_path = self.process_label_substitutions( project_path )
        self.project_label, self.folder_path = self.decompose_project_path( project_path )

        mimetypes= self.action_parameters.get( 'mimeTypes', 'any' )
        mimetypes = self.process_label_substitutions( mimetypes )
        mimetypes = [ x.strip( ) for x in mimetypes.split( ',' ) ]
        self.mimetypes_to_include = mimetypes

        self.purge_included_documents = False
        purge_flag = self.action_parameters.get( 'purgeIncludedDocuments', 'NO' )
        purge_flag = self.process_label_substitutions( purge_flag )
        if purge_flag.upper( ) == 'YES':
            self.purge_included_documents = True

    def do_epilogue(self):
        pass
