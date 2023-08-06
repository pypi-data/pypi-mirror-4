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
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand


class XPathMerge(ActionCommand):
    __domain__ = "action"
    __operation__ = "xpath-merge"
    __aliases__   = [ 'xpathMergeAction', 'xpathMerge' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        doc_a = etree.parse(self.rfile)
        message = self._ctx.run_command('message::get', process=self.process,
                                                        label=self._input_label)
        self.log.debug('Merging with message {0}'.format(message.uuid))
        input_handle = self._ctx.run_command('message::get-handle', object=message)
        doc_b = etree.parse(input_handle)
        root_a = doc_a.getroot()
        elements = doc_b.xpath(self._xpath, namespaces=doc_b.getroot().nsmap)
        self.log.debug('Merging {0} elements from message.'.format(len(elements)))
        for element in elements:
            root_a.append(element)
        self.log.debug('Document merge complete, writing output.')
        self.wfile.write(etree.tostring(root_a))
        doc_b = None
        doc_a = None
        input_handle.close()

    def parse_action_parameters(self):
        self._input_label = self.action_parameters.get('label', None)
        self._xpath       = self.action_parameters.get('xpath', None)
        if (self._xpath is None):
            raise CoilsException('No path provided for xpath query')
        else:
            self._xpath = self.decode_text(self._xpath)

    def do_epilogue(self):
        pass
