#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core           import NotImplementedException
from filter               import OpenGroupwareServerSideFilter

MARKDOWN_ENABLED=False
try:
    import markdown
    MARKDOWN_ENABLED = True
except:
    pass

if MARKDOWN_ENABLED:

    class MarkdownOSSF(OpenGroupwareServerSideFilter):

        @property
        def handle(self):
            wfile = BLOBManager.ScratchFile()
            if self._mimetype not in ( 'text/plain' ):
                raise Exception( 'Input stream is not a text document')
            markdown.markdownFromFile( input=self._rfile, output=wfile, safe_mode='escape' )
            wfile.seek( 0 )
            return wfile

        @property
        def mimetype(self):
            return 'text/html'

else:

    class MarkdownOSSF(OpenGroupwareServerSideFilter):

        @property
        def handle(self):
            raise NotImplementedException( 'Markdown support is not available' )

        @property
        def mimetype(self):
            raise NotImplementedException( 'Markdown support is not available' )
