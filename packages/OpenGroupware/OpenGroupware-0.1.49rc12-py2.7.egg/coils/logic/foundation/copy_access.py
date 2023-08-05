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
from sqlalchemy         import *
from coils.core         import *

# Issue#144 : Implement object::copy-access
class CopyObjectACLs(Command):
    __domain__ = "object"
    __operation__ = "copy-access"

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        self._source = params.get('source', None)
        self._target = params.get('target', None)
        if (self._source is None) or (self._target is None):
            raise CoilsException('Either source or target not provided to object::copy-access')

    def run(self, **params):
        acls = self._ctx.run_command('object::get-access', object=self._source)
        if (len(acls) > 0):
            for acl in acls:
                self._ctx.run_command('object::get-access', object=self._source)
