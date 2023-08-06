#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
import time
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand

class ListEnterprises(GetCommand):
    __domain__ = "enterprise"
    __operation__ = "list"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._props = params.get('properties', [ Enterprise.object_id,
                                                 Enterprise.version,
                                                 Enterprise.name ] )
        self._contexts = params.get('contexts', None)
        self._mask     = params.get('mask', 'r')
        self._limit    = params.get('limit', None)

    def run(self):
        manager = BundleManager.get_access_manager('Enterprise', self._ctx)
        self._result = manager.List(self._ctx, self._props, contexts=self._contexts,
                                                            mask=self._mask,
                                                            limit=self._limit)
