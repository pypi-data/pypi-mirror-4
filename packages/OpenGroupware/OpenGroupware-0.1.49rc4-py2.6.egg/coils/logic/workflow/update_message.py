#
# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
# JUSTIFICATION[os]: Application may request that OIE read in a message's
#                    contents from an absolute file path.  HOWEVER, internally
#                    message contents should ALWAYS be passed to message::set
#                    using the "handle" directive, and than description should
#                    have been acquired via the use of BLOBManager.
import os, shutil
from coils.core          import *
from shutil              import copyfileobj
from utility             import filename_for_message_text

class UpdateMessage(Command):
    __domain__ = "message"
    __operation__ = "set"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        # Object
        if ('object' in params):
            self.obj = params.get('object')
        else:
            raise CoilsException('Update of a message requires a message')
        # Data / Filename
        if ('data' in params):
            self.source = 'data'
            self.data = params['data']
        elif ('filename' in params):
            self.source = 'handle'
            self.handle = os.open(params['filename'], 'rb')
        elif ('handle' in params):
            self.source = 'handle'
            self.handle = params['handle']
        else:
            raise CoilsException('No message data or source specified')
        # Other...
        self._mimetype = params.get('mimetype', self.obj.mimetype)
        self._label    = params.get('label', self.obj.label)

    def run(self):
        #db = self._ctx.db_session()
        self.obj.label    = self._label
        self.obj.mimetype = self._mimetype
        self.obj.version  = (self.obj.version + 1)
        self.obj.status   = 'updated'
        self.obj.modified = self._ctx.get_utctime()
        try:
            text = BLOBManager.Create(filename_for_message_text(self.obj.uuid), encoding='binary')
            if (self.source == 'data'):
                text.write(self.data)
            if (self.source == 'handle'):
                self.handle.seek(0)
                # Copy file to message_id
                shutil.copyfileobj(self.handle, text)
            BLOBManager.Close(text)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Failure to allocate message contents')
        self.obj.size = BLOBManager.SizeOf(filename_for_message_text(self.obj.uuid))
        self._result = self.obj
