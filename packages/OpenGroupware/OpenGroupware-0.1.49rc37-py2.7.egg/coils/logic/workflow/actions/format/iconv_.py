#
# Copyright (c) 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
import codecs, shutil
from coils.core          import CoilsException
from coils.core.logic    import ActionCommand

VALID_ERROR_POLICIES= ( 'strict', 'replace', 'ignore', 'xmlcharrefreplace', 'backslashreplace', )

class IConvAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "codepage-convert"
    __aliases__   = [ 'iConvAction', 'iconvAction', 'iconv' ]

    @property
    def result_mimetype(self):
        self.input_message.mimetype

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        filter = codecs.EncodedFile( self.wfile, self.input_encoding, self.output_encoding, self.error_policy )
        shutil.copyfileobj( self.rfile, filter )

    def parse_action_parameters(self):
        self.input_encoding = self._params.get( 'inputEncoding', 'utf8' ).lower( )
        self.output_encoding = self._params.get( 'outputEncoding', 'ascii' ).lower( )
        self.error_policy = self._params.get( 'errorPolicy', 'ignore' ).lower( )

        if self.error_policy not in VALID_ERROR_POLICIES:
            raise CoilsException( 'Invalid code-page conversion error policy: "{0}"'.format( self.error_policy ) )


