#
# Copyright (c) 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core          import *
from coils.foundation    import *
from coils.core.logic    import UpdateCommand
from keymap              import COILS_ROUTEGROUP_KEYMAP

class UpdateRouteGroup(UpdateCommand):
    __domain__ = "routegroup"
    __operation__ = "set"

    def __init__(self):
        UpdateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap =  COILS_ROUTEGROUP_KEYMAP
        self.entity = RouteGroup
        UpdateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        UpdateCommand.parse_parameters( self, **params )

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command( 'routegroup::get', id=object_id,
                                                         access_check=access_check)

    def check_run_permissions(self):
        if ( self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN ) or
             self._ctx.has_role( OGO_ROLE_WORKFLOW_ADMIN ) or
             self._ctx.has_role( OGO_ROLE_WORKFLOW_DEVELOPERS ) ):
            rights = self._ctx.access_manager.access_rights( self.obj, contexts=self.context_ids )
            if not set( 'wa' ).intersection( rights ):
                raise AccessForbiddenException( 'Insufficient access to {0}'.format( self.obj ) )
            return
        else:
            raise AccessForbiddenException( 'Context lacks role; cannot modify workflow route groups.' )

    def run(self):
        UpdateCommand.run(self)
        self.set_result( self.obj )
