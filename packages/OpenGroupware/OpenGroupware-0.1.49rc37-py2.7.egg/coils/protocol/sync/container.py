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
# THE SOFTWARE.
#
from coils.core     import *
from coils.net      import PathObject
from sync           import SyncSync
from items          import SyncItems
from keys           import SyncKeys

class SyncContainer(PathObject):
    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def authenticate(self):
        pass

    def object_for_key(self, name):
        if (self.authenticate()):
            if (name == 'sync'): return SyncSync(self)
            elif (name == 'keys'): return SyncKeys(self)
            elif (name == 'items'): return SyncItems(self)

class ContactsContainer(SyncContainer):

    def __init__(self, parent, **params):
        SyncContainer.__init__(self, parent, **params)

    def load_contacts(self):
        pass