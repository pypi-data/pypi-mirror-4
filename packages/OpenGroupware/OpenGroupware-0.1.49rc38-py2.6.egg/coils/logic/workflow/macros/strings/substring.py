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
import re
from coils.core                   import *
from coils.core.logic             import MacroCommand

class SubstringMacro(MacroCommand):
    __domain__ = "macro"
    __operation__ = "substring"

    @property
    def descriptor(self):
        return { 'name': 'substring',
                 'parameters': { 'var1': {'type': 'any'},
                                 'var2': {'type': 'any'} },
                 'help': 'Returns substring if found from original string' }

    def parse_parameters(self, **params):
        MacroCommand.parse_parameters(self, **params)
        self._var1 = params.get('var1', None)
        self._var2 = params.get('var2', None)
        if (self._var1 is None) or (self._var2 is None):
            raise CoilsException('NULL input provided to substring macro')

    def run(self):
        m = re.search(str(self._var2), str(self._var1))
        if m:
            self.set_result(str(self._var1)[m.start():m.end()])
        else:
            self.set_result('')

