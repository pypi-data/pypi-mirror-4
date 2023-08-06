#
# Copyright (c) 2010, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
    # TODO: Set an appropriate result_mimetype based upon the results of
    #       of the operation; which may produce either text or XML.
    __domain__ = "action"
    __operation__ = "xpath"
    __aliases__   = [ 'xpathAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        doc = etree.parse(self.rfile)
        nsmap = doc.getroot().nsmap
        if None in nsmap:
            nsmap['default'] = nsmap[None]
            nsmap.pop( None )
        result = doc.xpath(self._xpath, namespaces=nsmap)
        if (len(result) > 0):
            if (isinstance(result[0], basestring)):
                for x in result:
                    self.wfile.write(x)
            else:
                self.wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
                self.wfile.write(u'<ResultSet formatName=\"_xpath\" className=\"\">')
                for x in result:
                    self.wfile.write(u'<result dataType=\"xml\" isPrimaryKey=\"False\">')
                    self.wfile.write(etree.tostring(x))
                    self.wfile.write(u'</result>')

    def parse_action_parameters(self):
        self._xpath     = self.action_parameters.get('xpath', None)
        if (self._xpath is None):
            raise CoilsException('No path provided for xpath query')
        else:
            self._xpath = self.decode_text(self._xpath)

    def do_epilogue(self):
        pass

