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
from format import Format
from format import COILS_FORMAT_DESCRIPTION_OK
from format import COILS_FORMAT_DESCRIPTION_INCOMPLETE

class LineOrientedFormat(Format):

    def __init__(self):
        Format.__init__(self)
        self.in_counter = 0
        self.out_counter = 0

    def set_description(self, fd):
        code = Format.set_description(self, fd)
        if (code[0] == 0):
            self.description = fd
            self._definition    = self.description.get('data')
            for field in self.description['data']['fields']:
                if not ('kind' in field):
                    return (COILS_FORMAT_DESCRIPTION_INCOMPLETE, 'Incomplete Description:' \
                                           ' kind missing from <{0}> field'.format(field['name']))
            self._skip_comment   = bool(self._definition.get('skipCommentedLines', False))
            self._skip_lines     = int(self._definition.get('skipLeadingLines', 0))
            self._skip_blanks    = bool(self._definition.get('skipBlankLines', False))
            self._line_delimiter = self._definition.get('lineDelimiter', (0x0D, 0x0A))
            self._discard_on_error = self._definition.get('discardMalformedRecords', False)
            self._allowed_ords   = self._definition.get('allowedNonprintableOrdinals', (0x09, 0x0A, 0x0D))
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')
        else:
            return code

    def next_record_in(self):
        ''' Read a single line of input, return None if no more lines are available. '''
        x = self._input.readline()
        if (len(x) == 0):
            return None
        return x
