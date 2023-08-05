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
try:
    from PIL import Image
except:
    HAS_PIL = False
else:
    HAS_PIL = True

import json
from coils.core    import NotImplementedException, \
                           BLOBManager
from filter       import OpenGroupwareServerSideFilter

if HAS_PIL:
    class ImageThumbnailOSSFilter(OpenGroupwareServerSideFilter):

        @property
        def handle(self):
            if (self._mimetype not in ('image/jpeg', 'image/png')):
                raise Exception('Input type for thumbnail is not a supported image type')
            self.image = Image.open(self._rfile)
            if (hasattr(self, '_width')):
                width = int(self._width)
            else:
                width = self.image.size[0]
            if (hasattr(self, '_height')):
                height = int(self._height)
            else:
                height = self.image.size[1]
            s = BLOBManager.ScratchFile()
            self.image.thumbnail((width, height), Image.ANTIALIAS)
            self.image.save(s, self.image.format)
            s.seek(0)
            return s

        @property
        def mimetype(self):
            return self._mimetype

else:
    class ImageThumbnailOSSFilter(OpenGroupwareServerSideFilter):

        @property
        def handle(self):
            return self._rfile

        @property
        def mimetype(self):
            return self._mimetype