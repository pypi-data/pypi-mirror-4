#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from ftplib              import FTP
from shutil              import copyfileobj
from coils.core          import *
from coils.core.logic    import ActionCommand

class FTPPutFileAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "ftp-put-file"
    __aliases__   = [ 'ftpPutFile', 'ftpPutFileAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def authentication_callback(self, server, share, workgroup, username, password):
        return (self._domain_string, self._username_string, self._password_string)

    def do_action(self):
        
        ftp = FTP(self._hostname)
        
        ftp.set_pasv(self._passive)
        
        if not self._username:
            ftp.login()
        else:
            ftp.login(self._username, self._password)

        if self._directory:
            ftp.cwd(self._directory)
            
        ftp.storbinary('STOR {0}'.format(self._filename), self._rfile)
        
        ftp.quit()

    def parse_action_parameters(self):
        
        self._hostname = self.process_label_substitutions(self.action_parameters.get('server'))
        self._filename = self.process_label_substitutions(self.action_parameters.get('filename'))

        self._passive  = self.process_label_substitutions(self.action_parameters.get('passive', 'YES'))
        if not self._passive.upper() == 'NO':
            self._passive = True
        else:
            self._passive = False

        self._username = self.action_parameters.get('username', None)
        if self._username:
            self._username = self.process_label_substitutions(self._username)
            self._password = self.action_parameters.get('password', '$__EMAIL__;')
            self._password = self.process_label_substitutions(self._password)
            
        self._directory = self.action_parameters.get('directory', None)
        if self._directory:
            self._directory = self.process_label_substitutions(self._directory)

    def do_epilogue(self):
        pass
