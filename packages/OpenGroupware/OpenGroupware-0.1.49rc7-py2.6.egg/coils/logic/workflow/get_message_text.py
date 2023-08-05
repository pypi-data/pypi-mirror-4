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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from utility            import filename_for_message_text

class GetMessageText(Command):
    __domain__ = "message"
    __operation__ = "get-text"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        # TODO: We should have the option to return the file stream
        # for dealing with large messages.
        Command.parse_parameters(self, **params)
        self._scope = params.get('scope', [])
        if ('object' in params):
            self._uuid = params['object'].uuid
        elif ('uuid' in params):
            self._uuid = params.get('uuid', None)
        elif (('label' in params) and ('process' in params)):
            self._uuid    = None
            self._label   = params.get('label')
            self._process = params.get('process')

    def run(self):
        # WARN: Security not implemented!
        # TODO: Verify message, and access to message
        # TODO: We can no longer retrieve message text via UUID??
        # TODO: Should we do something magical about mime type?
        if (self._uuid is None):
            pid = self._process.object_id
            db  = self._ctx.db_session()
            # Walk the scopes looking for the message in question
            scopes = self._scope[:]
            scopes.reverse()
            scopes.append(None)
            for scope in scopes:
                self.log.debug('Search for label {0} in scope {0}'.format(self._label, scope))
                query = db.query(Message).filter(and_(Message.label == self._label,
                                                       Message.process_id == pid,
                                                       Message.scope == scope))
                data = query.all()
                if (len(data) > 0):
                    self._uuid = data[0].uuid
                    break
        if (self._uuid is None):
            raise CoilsException('message::get-text found no message for label "{0}"'.format(self._label))
        handle = BLOBManager.Open(filename_for_message_text(self._uuid), 'rb')
        self._result = handle.read()
        BLOBManager.Close(handle)
