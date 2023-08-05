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
#
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

class SetValueAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "set-value"
    __aliases__   = [ 'setValue', 'setValueAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        doc = etree.parse(self.rfile)
        for element in doc.xpath(self._xpath, namespaces=doc.getroot().nsmap):
            source.text = self._value
        self.wfile.write(etree.tostring(doc))

    def parse_action_parameters(self):
        self._xpath     = self.action_parameters.get('xpath', None)
        if (self._xpath is not None):
            self._xpath = self.decode_text(self._xpath)
            self._xpath = self.process_label_substitutions(self._xpath)
        else:
            self._value     = self.action_parameters.get('value', None)
            if (self._value is None):
                raise CoilsException('No value or xpath provided for setValueAction.')
            else:
                self._value = self.process_label_substitutions(self._value)

    def do_epilogue(self):
        pass
