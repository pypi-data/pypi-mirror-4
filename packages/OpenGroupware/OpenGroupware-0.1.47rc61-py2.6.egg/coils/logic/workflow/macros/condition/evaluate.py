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
from command                      import EvaluationCommand

class EvaluateMapMacro(MacroCommand, EvaluationCommand):
    __domain__ = "macro"
    __operation__ = "evaluate"

    @property
    def descriptor(self):
        return { 'name': 'evaluate',
                  'parameters': { 'operator': { 'type': 'string', 'values': [ '>',
                                                                              '>=',
                                                                              '<',
                                                                              '<=',
                                                                              '=',
                                                                              '!=',
                                                                              'equals',
                                                                              'caseIgnoreEquals'] },
                                  'var1':     { 'type': 'any'},
                                  'var2':     { 'type': 'any'} },
                  'help': 'Compare var1 and var2 using operator; output boolean True or False' }

    def parse_parameters(self, **params):
        # TODO: Implement
        raise NotImplementedException('Class not implmented')

    def run(self):
        if (self.evaluate(self._operator, self._var1, self._var2)):
            self.set_result(True)
        else:
            self.set_result(False)
