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
import base64
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

class XPathTestAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "xpath-test"
    __aliases__   = [ 'xpathTestAction', 'xpathTest' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def do_action(self):
        #TODO: Do we have to DOM the document in order to perform the xpath?
        #WARN: This probably works badly, and slowly, for large documents.
        doc = etree.parse(self.rfile)
        result = doc.xpath(self._xpath, namespaces=doc.getroot().nsmap)
        if (len(result) > 0):
            self.wfile.write(u'YES')
        else:
            self.wfile.write(u'NO')
        result = None
        doc = None

    def parse_action_parameters(self):
        self._xpath     = self.action_parameters.get('xpath', None)
        self._b64       = self.action_parameters.get('isBase64', 'NO').upper()
        if (self._xpath is None):
            raise CoilsException('No path provided for xpath query')
        else:
            if (self._b64 == 'YES'):
                self.xpath = base64.decodestring(self._xpath.strip())
            else:
                self.xpath = self.decode_text(self._xpath)
        self._xpath = self.process_label_substitutions(self._xpath)

    def do_epilogue(self):
        pass
