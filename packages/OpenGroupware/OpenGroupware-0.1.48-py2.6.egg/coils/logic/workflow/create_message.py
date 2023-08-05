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
import shutil
from coils.core          import *
from coils.foundation    import *
from shutil              import copyfile
from utility             import *

class CreateMessage(Command):
    __domain__ = "message"
    __operation__ = "new"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.label = params.get('label', None)
        self.do_rewind = params.get('rewind', True)
        self.mimetype = params.get('mimetype', 'application/octet-stream')
        if ('process_id' in params):
            self.process_id = int(params['process_id'])
        elif ('process' in params):
            self.process_id = params['process'].object_id
        else:
            raise CoilsException('Creation of a message requires a process')
        if ('scope' in params):
            self.scope = params.get('scope')
        else:
            self.scope = None
        if ('data' in params):
            self.handle = None
            self.data = params['data']
        elif ('filename' in params):
            self.handle = open(params['filename'], 'rb')
        elif ('handle' in params):
            self.handle = params['handle']
        else:
            raise CoilsException('No message data or source specified')

    def run(self):
        db = self._ctx.db_session()
        message = Message(self.process_id)
        message.scope = self.scope
        message.mimetype = self.mimetype
        utc_time =  self._ctx.get_utctime()
        message.modified = utc_time
        message.created = utc_time
        # Label the message
        if (self.label is None):
            if (message.scope is None):
                self.log.debug('Creating unlabeled message {0} with global scope in process {1}'.\
                  format(message.uuid, message.process_id))
            else:
                self.log.debug('Creating unlabeled message {0} with scope {1} in process {2}'.\
                  format(message.uuid, message.scope, message.process_id))
        else:
            message.label = self.label
            if (message.label in ['OutputMessage', 'InputMessage', 'Exception']):
                message.scope = None
            if (self.scope is None):
                self.log.debug('Creating message {0} labeled {1} with global scope in process {2}'.\
                    format(message.uuid, message.label, message.process_id))
            else:
                self.log.debug('Creating message {0} labeled {1} with scope {2} in process {3}'.\
                    format(message.uuid, message.label, message.scope, message.process_id))
        try:
            message_file = BLOBManager.Create(filename_for_message_text(message.uuid), encoding='binary')
            if (self.handle is None):
                if (self.data is not None):
                    message_file.write(self.data)
            else:
                if self.do_rewind:
                    self.handle.seek(0)
                else:
                    self.log.debug('Rewind of stream before content copy is disabled')
                shutil.copyfileobj(self.handle, message_file)
            BLOBManager.Close(message_file)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Failure to allocate message contents')
        message.size = BLOBManager.SizeOf(filename_for_message_text(message.uuid))
        self._ctx.db_session().add(message)
        self._result = message
