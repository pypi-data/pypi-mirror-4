#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.foundation     import BLOBManager
from coils.foundation.api.pypdf import PdfFileReader
from filter               import OpenGroupwareServerSideFilter


class PDFToTextOSSFilter(OpenGroupwareServerSideFilter):

    @property
    def handle(self):
        wfile = BLOBManager.ScratchFile()
        if (self._mimetype not in ('application/pdf')):
            raise Exception('Input stream is not a PDF document')
        self.log.debug('Reading PDF stream started')
        pdf = PdfFileReader(self._rfile)
        for i in range(0, pdf.getNumPages()):
            self.log.debug('Reading text from page {0} of input stream'.format(i))
            text = pdf.getPage(i).extractText().replace(u'\xa0', ' ')
            text = text.encode('ascii', 'xmlcharrefreplace')
            wfile.write(text)
        self.log.debug('Reading PDF stream complete')
        wfile.seek(0)
        return wfile

    @property
    def mimetype(self):
        return 'text/plain'
