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
import errno
from coils.core          import *
from coils.core.logic    import ActionCommand
from command             import SSHAction

class SSHExecAction(ActionCommand, SSHAction):
    __domain__ = "action"
    __operation__ = "ssh-exec"
    __aliases__   = [ 'sshExecuteCommandAction', 'sshExecAction', 'sshExec', 'sshExecuteCommand' ]
    mode = None

    def __init__(self):
        ActionCommand.__init__(self)
        
    @property
    def result_mimetype(self):
        return self._mimetype

    def parse_action_parameters(self):                
        ActionCommand.parse_action_parameters( self )
        
        SSHAction.parse_action_parameters( self )
        
        self._command  = self.action_parameters.get( 'command', None )
        self._filename = self.action_parameters.get( 'filePath', None )
        self._mimetype = self.action_parameters.get( 'mimeType', 'application/octet-stream' )
            
        if not self._command:
            raise CoilsException( 'No command string for executeSSHCommand action' )        
        
        self._command      = self.process_label_substitutions( self._command )
           
        if self._filename:
            self._filename = self.process_label_substitutions( self._filename )

    def do_action(self):
        self.initialize_client( )
        private_key = self.initialize_private_key( path=self.path_to_private_key( ), password=self._secret )
        transport = self.initialize_transport( self._hostname, self._hostport )
        if self.authenticate( transport = transport, username=self._username, private_key=private_key ):
            self.run_command( transport=transport, command=self._command, wfile=self.wfile )
            if self._filename:
                try:
                    self.get_file( transport=transport, path=self._filename, wfile=self.wfile )
                except IOError, e:
                    if e.errno == errno.ENOENT:
                        raise CoilsException( 'Path "{0}" on host "{1}" not found; could not retrieve file.'.format( self._filename, self._hostname ) )
                    else:
                        raise e
        else:
            raise CoilsException( 'Unable to complete SSH authentication' )
        self.close_transport( transport=transport )
