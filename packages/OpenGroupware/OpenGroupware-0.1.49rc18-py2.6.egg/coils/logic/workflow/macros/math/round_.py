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
# THE SOFTWARE.
#
from coils.core                   import *
from coils.core.logic             import MacroCommand

class RoundMacro(MacroCommand):
    __domain__ = "macro"
    __operation__ = "round"

    @property
    def descriptor(self):
        return { 'name': 'round',
                  'parameters': { 'var1': {'type': 'numeric'},
                                  'precision': {'type': 'numeric'} },
                  'help': 'Round given value to digits set by precision' }

    def parse_parameters(self, **params):
        MacroCommand.parse_parameters(self, **params)
        self._var1 = params.get('var1', None)
        self._precision = params.get('precision', None)
        if (self._var1 is None) or (self._precision is None):
            raise CoilsException('NULL input provided to round macro')
        if( not isinstance(self._var1,(int, float))):
            raise CoilsException('Non-numeric value provided to round macro')
        else:
            self._var1 = float(self._var1)
        if( not isinstance(self._precision,(int))):
            raise CoilsException('Non-numeric or Non-integer value provided to round macro in presicion')

    def run(self):
        self.set_result(round(self._var1,self._precision))

