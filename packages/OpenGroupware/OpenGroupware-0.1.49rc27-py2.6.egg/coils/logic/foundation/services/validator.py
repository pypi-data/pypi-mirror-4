#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from time             import time
from sqlalchemy       import *
from sqlalchemy.orm   import *
from coils.core       import *

class ManagerService(Service):
    __service__ = 'coils.validator'
    __TimeOut__ = 60

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._enabled  = True
        self._ctx = AdministrativeContext({}, broker=self._broker)
        self._last_time = time()

    def work(self):
        if (self._enabled):
            if ((time() - self._last_time) > 360):
                self.log.debug('Running validator processes')
                self._scan_running_processes()
                self._start_queued_processes()
                self._last_time = time()

    def _generate_checksum(self):
        db = self._ctx.db_session()
        blobs = db.query(DocumentVersion).filter(DocumentVersion.checksum is None).limit(10)
        for blob in blobs:
            # TODO: read the handle to verify the checksum
            pass

    def _verify_checksum(self, handle):
        # TODO: read the handle and verify the checksum
        pass

