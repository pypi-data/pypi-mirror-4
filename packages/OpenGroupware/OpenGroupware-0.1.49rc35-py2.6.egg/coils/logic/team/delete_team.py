#
# Copyright (c) 2011, 2013
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
from sqlalchemy       import *
from sqlalchemy.orm   import *
from coils.core       import *
from coils.core.logic import DeleteCommand

class DeleteTeam(DeleteCommand):
    __domain__ = "team"
    __operation__ = "delete"

    def check_run_permissions(self):
        if self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN ):
            return
        raise  AccessForbiddenException( 'Context lacks administrative role; cannot delete a team' )

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command( 'team::get', id=object_id,
                                                   access_check=access_check )

    def delete_membership(self):
        members = self.obj.members
        for assignment in members:
            self.delete_object_info(assignment)
            self._ctx.db_session().delete(assignment)

    def run(self):
        self.delete_membership()
        DeleteCommand.run(self)
        self.set_return_value( True )
