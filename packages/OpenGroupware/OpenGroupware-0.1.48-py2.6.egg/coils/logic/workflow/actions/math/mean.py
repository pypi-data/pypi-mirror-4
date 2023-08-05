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
import os, base64
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand


class XPathAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "mean"
    __aliases__   = [ 'meanAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def _calculate_arithmatic_mean(self, values):
        total = 0.0
        count = 0.0
        for value in values:
            total = total + float(value)
            count = count + 1.0
        return (total / count)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def do_action(self):
        result = None
        doc = etree.parse(self.rfile)
        values = doc.xpath(self._xpath)
        if (isinstance(result, list)):
            if (self._kind == 'ARITHMATIC'):
                result = self._calculate_arithmatic_mean(values)
        self.wfile.write(str(result))

    def parse_action_parameters(self):
        self._xpath     = self.action_parameters.get('xpath', None)
        self._kind      = self.action_parameters.get('kind', 'ARITHMATIC').upper()
        if (self._xslt is None):
            raise CoilsException('No path provided for xpath query')
        else:
            self._xpath = self.decode_text(self._xpath)

    def do_epilogue(self):
        pass
