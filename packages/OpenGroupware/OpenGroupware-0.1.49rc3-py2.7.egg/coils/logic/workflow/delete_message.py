#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
#from coils.model         import *
from utility             import filename_for_message_text

class DeleteMessage(Command):
    __domain__ = "message"
    __operation__ = "delete"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('uuid' in params):
            self.id_type = 'uuid'
            self.uuid = params['uuid']
        elif (('label' in params) and (('process' in params) or
                                        ('pid' in params))):
            self.id_type = 'label'
            self.label = params['label']
            if ('process' in params):
                self.pid = params['process'].object_id
            else:
                self.pid = int(params['pid'])
        else:
            raise CoilsException('message::get parameters do not identify a message.')

    def run(self):
        db = self._ctx.db_session()
        if (self.id_type == 'uuid'):
            query = db.query(Message).filter(Message.uuid==self.uuid)
        else:
            # Query for Message by label; labels are unique within a process.
            query = db.query(Message).filter(and_(Message.label == self.label,
                                                   Message.process_id == self.pid))
        data = self._ctx.access_manager.filter_by_access('r', query.all())
        for message in data:
            uuid = message.uuid
            self._ctx.db_session().delete(message)
            # TODO: Support message archiving rather than just deleting.
            #os.rename(filename_for_message_text(uuid),
            #          filename_for_deleted_message_text(uuid))
            BLOBManager.Delete(filename_for_message_text(uuid))
