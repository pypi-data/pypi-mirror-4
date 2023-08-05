#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import os, re
from datetime            import datetime
from xml.sax.saxutils    import escape, unescape
from tempfile            import mkstemp
from coils.core          import Command, CoilsException
from coils.foundation    import AuditEntry, BLOBManager

class AsyncronousCommand(Command):

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._callback = params.get('callback', None)
        self._timeout = params.get('timeout', 1000)
        self._raise_error = params.get('raise_error', True)
        
    def parse_success_response(self, data):
        pass
        
    def parse_failure_response(self, data):
        pass

    def local_callback(self, uuid, source, target, data):
        if self._callback:
            return self._callback(uuid, source, target, data)
        else:
            if 'status' in data:
                if data['status'] == 200:
                   self.parse_success_response(data)
                else:
                    if self._raise_error:
                        if 'text' in data:
                            raise CoilsException(data['text'])
                        else:
                            raise CoilsException('Received failure from "{0}" of "{1}" but no description.'.format(source, data['status']))
                    else:
                        self.parse_failure_response(data)
            else:
                raise CoilsException('Received response from "{0}" with no status indication.'.format(source))
        return True
        
    def callout(self, target, payload):
        return self._ctx.send(None, target, payload, callback=self.local_callback)
        
    def wait(self):
        if not self._callback:
            self._ctx.wait(self._timeout) 
