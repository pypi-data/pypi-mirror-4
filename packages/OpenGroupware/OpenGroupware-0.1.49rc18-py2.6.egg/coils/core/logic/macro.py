#
# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core          import Command, CoilsException

class MacroCommand(Command):
    def __init__(self):
        Command.__init__(self)

    @property
    def descriptor(self):
        raise NotImplementedException('Macro descriptor not implemented.')

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._variables = params.get('variables', {})


    def get_variable(self, name):
        return self._variables(name, None)

    def set_variable(self, name, value):
        self._variables[name] = value

    def verify(self):
        return True

    def do_action(self):
        # Child MUST implement
        pass

    def run(self):
        self.parse_action_parameters()
        if (self.verify_action()):
            self.do_prepare()
            self.do_action()
            self.do_epilogue()
        else:
            raise CoilsException('Macro verification failed.')
        self._result = unicode(self._result)
