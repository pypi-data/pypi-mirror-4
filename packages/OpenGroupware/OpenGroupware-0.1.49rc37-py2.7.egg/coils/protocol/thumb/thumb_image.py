#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core           import *
from PIL import Image

class ThumbnailImage(object):

    def __init__(self, ctx, mimetype, entity, path):
        self.mimetype = mimetype
        self.context  = ctx
        self.entity   = entity
        self.pathname = path

    def create(self):

        if self.mimetype not in ( 'image/jpeg', 'image/png' ):
            raise Exception('Input type for thumbnail is not a supported image type' )

        rfile = self.context.run_command( 'document::get-handle', document=self.entity )
        if not rfile:
            return False

        self.image = Image.open( rfile )
        self.image.thumbnail( ( 175, 175), Image.ANTIALIAS )
        wfile = BLOBManager.Create( self.pathname.split( '/' ), 'binary' )
        self.image.save( wfile, 'png' )
        wfile.flush( )
        wfile.close( )
        del self.image
        return True

