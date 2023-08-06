#
# Copyright (c) 2009, 2012, 2013
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
#
import shutil, StringIO
from coils.core          import *
from coils.core.logic    import CreateCommand
from keymap              import COILS_ROUTEGROUP_KEYMAP

class CreateRouteGroup(CreateCommand):
    __domain__ = "routegroup"
    __operation__ = "new"

    def __init__(self):
        CreateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap = COILS_ROUTEGROUP_KEYMAP
        self.entity = RouteGroup
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)

    def check_run_permissions(self):
        if ( self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN ) or
             self._ctx.has_role( OGO_ROLE_WORKFLOW_ADMIN ) or
             self._ctx.has_role( OGO_ROLE_WORKFLOW_DEVELOPERS ) ):
            return
        raise AccessForbiddenException( 'Context lacks role; cannot create workflow route groups.' )

    def run(self, **params):
        CreateCommand.run(self, **params)
        self.save()
