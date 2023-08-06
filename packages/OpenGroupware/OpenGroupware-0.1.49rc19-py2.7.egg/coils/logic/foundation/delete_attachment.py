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
from coils.core          import *
from command            import AttachmentCommand

class DeleteAttachment(Command, AttachmentCommand):
    __domain__ = "attachment"
    __operation__ = "delete"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.uuid = params.get('uuid', None)
        if (self.uuid is None):
            raise CoilsException('attachment::delete parameters do not identify an attachment.')

    def run(self):
        db = self._ctx.db_session()
        query = db.query(Attachment).filter(Attachment.uuid==self.uuid)
        attachments = self._ctx.access_manager.filter_by_access('r', query.all())
        if (len(attachments) == 1):
            attachment = attachments[0]
            self._ctx.db_session().delete(attachment)
            BLOBManager.Delete(self.attachment_text_path(attachment))
        else:
            # TODO: Throw an error?
            pass

