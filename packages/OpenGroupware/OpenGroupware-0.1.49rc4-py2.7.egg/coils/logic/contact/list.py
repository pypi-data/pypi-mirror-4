#
# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
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

class ListContacts(GetCommand):
    __domain__ = "contact"
    __operation__ = "list"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        # TODO: Verify properties
        self._props = params.get('properties', [ Contact.object_id,  Contact.version,
                                                 Contact.first_name, Contact.last_name ] )
        # Get specified contexts
        self._contexts = params.get('contexts', self._ctx.context_ids)
        if (isinstance(self._contexts, int)):
            self._contexts = [ self._contexts ]
        elif (isinstance(self._contexts, basestring)):
            self._contexts = [ int(x.strip()) for x in self._contexts.split(',') ]
        elif (isinstance(self._contexts, list)):
            self._contexts = [ int(x) for x in self._contexts ]
        else:
            raise CoilsException('"contexts" parameter must be an integer, CSV list of integers, or list of integers')
        # Permissions mask
        self._mask     = params.get('mask', 'r')
        # Limit, if any.
        self._limit    = params.get('limit', None)

    def run(self):
        manager = BundleManager.get_access_manager('Contact', self._ctx)
        self._result = manager.List(self._ctx, self._props, contexts=self._contexts,
                                                            mask=self._mask,
                                                            limit=self._limit)
