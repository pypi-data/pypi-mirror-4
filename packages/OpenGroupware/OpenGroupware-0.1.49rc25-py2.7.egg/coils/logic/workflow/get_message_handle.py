#!/usr/bin/env python
# Copyright (c) 2009, 2012
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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from utility            import filename_for_message_text

class GetMessageHandle(Command):
    __domain__ = "message"
    __operation__ = "get-handle"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        # TODO: Support opening message via label & process
        Command.parse_parameters(self, **params)
        message = params.get( 'object', params.get( 'message', None ) )
        if message:
            self.uuid = message.uuid
        else:
            self.uuid = params.get('uuid', None)

    def run(self):
        # WARN: Security not implemented!
        # TODO: Verify message, and access to message
        self._result = None
        if self.uuid:
            message_file_path = '{0}/wf/m/{1}'.format( Backend.store_root( ), str( self.uuid ) )
            handle = BLOBManager.Open( filename_for_message_text( self.uuid ), 'rb', encoding='binary' )
            self.log.debug( 'Opened file {0} for reading.'.format( message_file_path ) )
            self._result = handle
        else:
            raise CoilsException( 'No message or UUID provided to message::get-handle' )
