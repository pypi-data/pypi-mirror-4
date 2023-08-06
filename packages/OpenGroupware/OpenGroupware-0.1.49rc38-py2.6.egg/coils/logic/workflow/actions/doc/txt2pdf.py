#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
from coils.core          import *
from coils.core.logic    import ActionCommand
from django1778          import pyText2Pdf

class TextToPDFAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "text-to-pdf"
    __aliases__   = [ 'textToPDF', 'textToPDFAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/pdf'

    def do_action(self):
        if self._do_ffs:
            self.log.debug('FFs in input will cause page breaks')
        self.log.debug('Columns: {0} TabWidth: {1} Size: {2}'.format(self._columns, self._tab_width, self._font_size))
        pdf = pyText2Pdf(self.rfile, self.wfile, title  = self._title,
                                                 font   = self._font,
                                                 ptSize = self._font_size,
                                                 tab    = self._tab_width,
                                                 cols   = self._columns,
                                                 do_ffs = self._do_ffs)
        pdf.Convert()

    def parse_action_parameters(self):
        self._columns   = int(self.process_label_substitutions(self.action_parameters.get('columns', '80'), default='80'))
        self._title     = self.process_label_substitutions(self.action_parameters.get('title', ''), default='')
        self._font_size = int(self.process_label_substitutions(self.action_parameters.get('pointSize', '10'), default='10'))
        self._tab_width = int(self.process_label_substitutions(self.action_parameters.get('tabWidth', '4'), default='4'))
        self._font      = self.process_label_substitutions(self.action_parameters.get('font', '/Courier'), default='/Courier')
        self._do_ffs    = self.process_label_substitutions(self.action_parameters.get('doFormFeeds', 'NO'), default='NO')
        if self._do_ffs.upper() == 'YES':
            self._do_ffs = 1
        else:
            self._do_ffs = 0

    def do_epilogue(self):
        pass
