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
#
# JUSTIFICATION[os]: Application may request that OIE read in a message's
#                    contents from an absolute file path.  HOWEVER, internally
#                    message contents should ALWAYS be passed to message::set
#                    using the "handle" directive, and than description should
#                    have been acquired via the use of BLOBManager.
from coils.core          import *

class UpdateAttachment(Command):
    __domain__ = "attachment"
    __operation__ = "set"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        # Object
        if ('attachment' in params):
            self.attachment = params.get('attachment')
        else:
            raise CoilsException('Update of a message requires a message')
        # Other...
        if ('related' in params):
            self.related_id = params.get('related').object_id
        else:
            self.related_id = params.get('related_id', self.attachment.related_id)
        self.mimetype = params.get('mimetype', self.attachment.mimetype)
        self.webdav_uid = params.get('webdav_uid', self.webdav_uid)

    def run(self):
        #db = self._ctx.db_session()
        self.attachment.webdav_uid = self.webdav_uid
        self.attachment.mimetype   = self.mimetype
        self.attachment.related_id = self.related_id
        self._result = self.attachment

