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
import shutil
from coils.core           import *

class ThumbnailFallback(object):

    def __init__(self, ctx, mimetype, entity, path):
        self.mimetype = mimetype
        self.context = ctx
        self.pathname = path

    def get_default(self):
        project = self.context.run_command( 'project::get', id=7000, access_check=False )
        if project:
            filename = self.mimetype.replace( '/', '-' )
            document = self.context.run_command( 'project::get-path', path='/Thumbnails/{0}.png'.format( filename ),
                                                                      project=project,
                                                                      access_check=False )
            if not document:
                document = self.context.run_command( 'project::get-path', path='/Thumbnails/application-octet-stream.png',
                                                                          project=project,
                                                                          access_check=False )
            if document:
                handle = self.context.run_command( 'document::get-handle', document=document )
                return handle
        return False
