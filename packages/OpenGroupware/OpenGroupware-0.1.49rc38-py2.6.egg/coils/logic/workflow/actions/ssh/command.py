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
import os   
# Justification for os import
#   We need to expand the path to the current user's home directory
#   in order to provide a reasonable default path to the SSH private
#   key
import shutil
import paramiko
from coils.core import CoilsException, ServerDefaultsManager

NO_PRIVATE_KEY_FOUND_MESSAGE =  '''No path provided to SSH private key; the 
 "OIESSHPrivateKeyPath" default was not set so the server attempted to find
 a filesystem object at ~/.ssh/id_dsa and then ~/.ssh/id_rsa but neither of
 these paths exist.  Either SSH is not configured for the OpenGroupware
 service user, the permissions are incorrect, or the administrator should 
 explicitly set the path to the intended private key by establishing a value
 for the  "OIESSHPrivateKeyPath" default. '''
 
INCORRECT_PRIVATE_KEY_PATH = '''The "OIESSHPrivateKeyPath" default specifies
 a path to the SSH private key of "{0}", but this 
 path does not exists or is not accessible.  Perhaps the value of the default
 is incorrect or filesystem permissions are incorrect.'''
 
UNABLE_TO_LOAD_PRIVATE_KEY = '''The SSH functions were unable to load the 
 private key from the path "{0}" using the provided 
 credentials although this path exists.  Double check credentials required
 to load the key or that this is a valid SSH private key.  
 Exception raised was: 
   {1}'''

class SSHAction(object):

    def initialize_client(self):
        ssh = paramiko.SSHClient( )
        ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy( ) )
        return ssh
        
    def path_to_private_key(self):
        sd = ServerDefaultsManager()
        key_path = sd.string_for_default( 'OIESSHPrivateKeyPath', value='' )
        if not key_path:
            key_path = os.path.expanduser( '~/.ssh/id_dsa' )
            if os.path.exists( key_path ):
                return key_path
            key_path = os.path.expanduser( '~/.ssh/id_rsa' )
            if os.path.exists:
                return key_path
            raise CoilsException( NO_PRIVATE_KEY_FOUND_MESSAGE )
        else:
            if os.path.exists( key_path ):
                return key_path
            raise CoilsException( INCORRECT_PRIVATE_KEY_PATH.format( key_path ) ) 
        
    def initialize_private_key(self, path, password):
        self.log_message( 'Loading private key from "{0}"'.format( path ), category='debug' )
        try:
            private_key = paramiko.DSSKey.from_private_key_file( path, password=password )
        except Exception, e:
            raise CoilsException( UNABLE_TO_LOAD_PRIVATE_KEY.format( path, e ) )
        else:
            return private_key

    def initialize_transport(self, hostname, port=22):
        # TODO: Add exception handling
        transport = paramiko.Transport( ( hostname, port ) )
        transport.set_keepalive( 30 )
        transport.start_client( )
        return transport
        
    def authenticate(self, transport, username, private_key):
        # TODO: Add exception handling
        transport.auth_publickey( username, private_key )
        return transport.is_authenticated
        
    def run_command(self, transport, command, wfile, truncate=True):
        # TODO: Add exception handling
        self.log_message( 'Attempting to execute "{0}" on remote host'.format( command ), category='debug' )
        channel = transport.open_session( )
        self.log_message( 'Channel created', category='debug' )
        stdout = channel.makefile( 'rb' )
        if truncate:
            wfile.seek ( 0 )
            wfile.truncate( )
            self.log_message( 'Output stream reset', category='debug' )
        # Channel will be automatically closed when command completes
        channel.exec_command( command )
        self.log_message( 'Command executed', category='debug' )
        shutil.copyfileobj( stdout, wfile )
        exit_status = channel.recv_exit_status()
        self.log_message( 'Command exit status is: {0}/{1}'.format( exit_status, type(exit_status) ), category='debug' )
        if exit_status != 0:
            # A non-zero exit status indicates failure
            self.log_message( 'Command execution failed', category='info' )
            raise CoilsException( 'Execution of command "{0}" failed on host "{1}"'.format( command, self._hostname ) )
        else:
            self.log_message( 'Command execution completed.', category='info' )
        return True

    def get_file(self, transport, path, wfile, truncate=True):
        # TODO: Add exception handling
        ftp = transport.open_sftp_client( )
        rfile = ftp.open( path )
        if truncate:
            wfile.seek ( 0 )
            wfile.truncate( )
        shutil.copyfileobj( rfile, wfile )
        wfile.flush()
        rfile.close()
        ftp.close()
        
    def put_file(self, transport, path, rfile, truncate=True):
        # TODO: Add exception handling
        # TODO: Test!
        ftp = transport.open_sftp_client( )
        wfile = ftp.open( path )
        if truncate:
            wfile.seek ( 0 )
            wfile.truncate( )
        shutil.copyfileobj( rfile, wfile )
        wfile.flush()
        rfile.close()
        ftp.close()        

    def close_transport(self, transport):
        transport.close( )
        
    def parse_action_parameters(self):        
        self._hostname = self.action_parameters.get('hostname', None)
        self._hostport = self.action_parameters.get('port', 22)
        self._secret   = self.action_parameters.get('passphrase', None)
        self._username = self.action_parameters.get('username', 'ogo')        

        if not self._hostname:
            raise CoilsException( 'No hostname specified for executeSSHCommand action' )

        self._hostname     = self.process_label_substitutions( self._hostname )
        self._hostport     = int( self.process_label_substitutions( self._hostport ) )
