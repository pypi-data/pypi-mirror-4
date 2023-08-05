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
import shutil
from coils.core          import *
from coils.foundation    import *
from coils.core.logic    import DeleteCommand
from utility             import *

class DeleteRoute(DeleteCommand):
    __domain__ = "route"
    __operation__ = "delete"

    def run(self):
        # TODO: Delete BPML files (markup).  But we need to be able to
        # schedule the deletion for a successful commit operation, otherwise
        # you can end up with a route in the DB with no corresponding markup.
        source = BLOBManager.Open(filename_for_route_markup(self.obj), 'rb', encoding='binary')
        target = BLOBManager.Create(filename_for_deleted_route_markup(self.obj), encoding='binary')
        if (source is not None) and (target is not None):
            shutil.copyfileobj(source, target)
            BLOBManager.Close(source)
            BLOBManager.Close(target)
            DeleteCommand.run(self)
        else:
            if (source is None):
                raise CoilsException('No route markup to delete for routeId#{0}'.format(self.obj.object_id))
            else:
                raise CoilsException('Unable to archive route markup for routeId#{0}'.format(self.obj.object_id))
        