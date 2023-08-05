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
import pickle, yaml
from sqlalchemy                   import *
from coils.core                   import *
from coils.foundation             import Route, Process, Message
from coils.logic.workflow.formats import Format

class CreateFormat(Command):
    __domain__ = "format"
    __operation__ = "new"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('description' in params):
            self.description = params.get('description')
            self.name      = self.description.get('name')
            self.classname = self.description.get('class')
        elif ('yaml' in params):
            self.description = yaml.load(params.get('yaml'))
            self.name      = self.description.get('name')
            self.classname = self.description.get('class')
        else:
            raise CoilsException('No description provided for data format')

    def run(self):
        format = Format.Marshall(self.classname)
        if (format is None):
            self.log.warn('No such format class as {0}'.format(self.classname))
            raise CoilsException('No such format class as {0}'.format(self.classname))
        code = format.set_description(self.description)
        if (code[0] < 0):
            self.log.warn('Format description error#{0}: {1}'.format(code[0], code[1]))
            raise CoilsException(code[1])
        format.save()
        self._result = format
        