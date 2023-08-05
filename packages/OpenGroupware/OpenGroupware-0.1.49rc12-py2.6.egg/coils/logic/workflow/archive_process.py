#
# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import shutil
from coils.core                   import *

#
# WARN: This command is implete!
# TODO: Implement
# How is this intended to be different than deleting a process?  Perhaps rather than
# deleting a process we can bundle it up into a ZIP file and store it in a project?
# That would require an object property that identifies a project for storage and
# potentially a path.... yes, this sounds like a really swell idea.  That archive
# can then be browsed and examined using simple filesystem projects.
# We can certainly use the TarFile module to move the data intoa tar file.
#

from utility import filename_for_versioned_process_code

class ArchiveProcess(Command):
    __domain__ = "process"
    __operation__ = "archive"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('process' in params):
            self._process = params.get('process').object_id
        elif ('pid' in params):
            self._process = self._ctx.run_command('process::get', id=int(params.get('pid')))
        else:
            raise CoilsException('Request to archive process with no PID')

    def run(self):
        get_filename = filename_for_versioned_process_code
        rfile = BLOBManager.Open(get_filename(self._process.object_id, self._process.version), 'r', encoding='binary')
        self._process.version += 1
        wfile = BLOBManager.Create(get_filename(self._process.object_id, self._process.version), encoding='binary')
        shutil.copyfileobj(rfile, wfile)
        BLOBManager.Close(rfile)
        BLOBManager.Close(wfile)
        self._process.status = 'archived'
        # TODO: Compress/Pack Messages ?
        self.set_return_value(True)
