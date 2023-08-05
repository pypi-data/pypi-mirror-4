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
from coils.core.logic    import ActionCommand

#TODO: Implement

class TransactionLoggerAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "log-transaction"
    __aliases__   = [ 'transactionLogger', 'transactionLoggerAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        pass

    @property
    def result_mimetype(self):
        return 'application/octet-stream'

    def parse_action_parameters(self):
        self._name     = self.action_parameters.get('mark')
        # logAll
        # size

    def do_epilogue(self):
        pass
