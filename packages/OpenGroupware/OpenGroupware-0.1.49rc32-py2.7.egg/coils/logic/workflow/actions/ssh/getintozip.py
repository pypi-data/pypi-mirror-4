#
# Copyright (c) 2012
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
import zipfile, shutil
from os.path             import basename
from tempfile            import NamedTemporaryFile
from coils.core          import *
from coils.core.logic    import ActionCommand
from command             import SSHAction

class SSHGetFilesIntoZipFileAction(ActionCommand, SSHAction):
    __domain__    = "action"
    __operation__ = "ssh-gets-files-to-zipfile"
    __aliases__   = [ 'sshGetFilesToZipAction', 'sshGetFilesToZip' ]
    mode = None

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def parse_action_parameters(self):
        ActionCommand.parse_action_parameters( self )

        SSHAction.parse_action_parameters( self )

        if self.action_parameters.get( 'skipMissing', 'YES' ).upper( ) == 'YES':
            self._skip_missing = True
        else:
            self._skip_missing = False

        if self.action_parameters.get( 'stripPath', 'YES' ).upper( ) == 'YES':
            self._strip_path = True
        else:
            self._strip_path = False

        self._filepaths = self.action_parameters.get( 'filePaths', None )
        self._filepaths = self.process_label_substitutions( self._filepaths )
        self._filepaths = [ x.strip( ) for x in self._filepaths.split( ',' ) ]

    def do_action(self):
        self.initialize_client( )
        private_key = self.initialize_private_key( path=self.path_to_private_key( ), password=self._secret )
        transport = self.initialize_transport( self._hostname, self._hostport )
        if self.authenticate( transport = transport, username=self._username, private_key=private_key ):
            ftp = transport.open_sftp_client( )
            # get many files
            zfile = zipfile.ZipFile( self.wfile, 'w', compression=zipfile.ZIP_DEFLATED )
            for filepath in self._filepaths:
                try:
                    rfile = ftp.open( filepath )
                except IOError as e:
                    if e.errno == 2 and self._skip_missing:
                        pass
                    else:
                        raise e
                else:
                    sfile = NamedTemporaryFile( delete=False )
                    shutil.copyfileobj( rfile, sfile )
                    sfile.flush( )
                    rfile.close( )
                    if self._strip_path:
                        zfile.write( sfile.name, arcname=basename( filepath ) )
                    else:
                        zfile.write( sfile.name, arcname=filepath )
                    sfile.close( )
            zfile.close( )
        else:
            raise CoilsException( 'Unable to complete SSH authentication' )
        self.close_transport( transport=transport )
