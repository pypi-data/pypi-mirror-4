#
# Copyright (c) 2010, 2012
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
from sqlalchemy         import *
from coils.core         import *
from get_access         import NO_ACL_ENTITIES

class SetACL(Command):
    __domain__ = "object"
    __operation__ = "set-acl"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if (('object' in params) or ('id' in params)):
            if ('object' in params):
                self._object_id = params.get('object').object_id
                self.obj = params.get('object')
            else:
                self._object_id = int(params.get('id'))
                self.obj = None
        else:
            raise CoilsException('No object specified for ACL creation.')
            
        # TODO: Verify value of "permissions"
        self._permissions = params.get('permissions', 'r')
        if self._permissions:
            self._permissions = self._permissions.lower().strip()
        else:
            self._permissions = None
            
        self._context_id  = int(params.get('context_id', self._ctx.account_id))
        # TODO: Verify value of "action; must be allowed or denied.
        self._action      = params.get('action', 'allowed').lower().strip()


    def run(self, **params):
        #TODO: Verify validity of permissions string
        #TODO: Verify context has write permissions to the object!
        if self.obj:
            kind = self.obj.__entityName__
        else:
            kind = self._ctx.type_manager.get_type(self._object_id)
        db = self._ctx.db_session()
        if (kind == 'Project'):
            if (self._action != 'allowed'):
                raise CoilsException('Access revocation not supported on Project entities.')
            acls =  db.query(ProjectAssignment).filter(and_(ProjectAssignment.parent_id == self._object_id,
                                                            ProjectAssignment.child_id == self._context_id)).all()
            if (len(acls) == 0):
                db.add(ProjectAssignment(self._object_id, self._context_id, permissions=self._permissions, info=None))
                self.set_result(True)
            elif (len(acls) == 1):
                acls[0].rights = self._permissions
                self.set_result(True)
            else:
                raise CoilsException('Inconsistency detected in ProjectAssignment data; multiple results.')
                self.set_result(False)
        elif kind == 'Unknown':
            self.set_result(False)
        else:
            # Everything other than Projects uses the ACL table for access controls
            # TODO: The object version of the entity should be bumped:
            # TODO: The ctag for the entity type should be bumpled
            acls = db.query(ACL).filter(and_(ACL.parent_id == self._object_id,
                                             ACL.action == self._action,
                                             ACL.context_id == self._context_id)).all()
            if acls:
                if len(acls) == 1:
                    if self._permissions:
                        acls[0].permissions = self._permissions
                    else:
                        db.delete(acls[0])            
                    self.set_result(True)
                else:
                    raise CoilsException('Inconsistency detected in ACL data; multiple results.')
                    self.set_result(False)
            else:
                # No matching pre-existing ACL exists - so lets create one
                if self._permissions:
                    acl = ACL(self._object_id, self._context_id, permissions=self._permissions, action=self._action)
                    db.add(acl)
                self.set_result(True)
