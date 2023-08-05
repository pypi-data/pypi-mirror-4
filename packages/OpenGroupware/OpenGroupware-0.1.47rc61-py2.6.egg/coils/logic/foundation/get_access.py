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
# THE SOFTWARE.
#
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import RETRIEVAL_MODE_SINGLE, \
                                RETRIEVAL_MODE_MULTIPLE

# This define is imported into set_access (object::set-access) as well
NO_ACL_ENTITIES = ['Unknown', 'Appointment', 'Resource', 'Participant']

class GetAccess(Command):
    __domain__ = "object"
    __operation__ = "get-access"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.object_ids = []
        if (('id' in params) or ('ids' in params)):
            if ('id' in params):
                self.mode = RETRIEVAL_MODE_SINGLE
                self.object_ids.append(int(params['id']))
            elif ('ids' in params):
                self.mode = RETRIEVAL_MODE_MULTIPLE
                for object_id in params['ids']:
                    self.object_ids.append(int(object_id))
        elif (('object' in params) or ('objects' in params)):
            if ('object' in params):
                self.mode = RETRIEVAL_MODE_SINGLE
                self.object_ids.append(int(params.get('object').object_id))
            elif ('objects' in params):
                self.mode = RETRIEVAL_MODE_MULTIPLE
                for o in params.get('objects'):
                    self.object_ids.append(int(o.object_id))
        else:
            raise CoilsException('No object specified for ACL retrieval')

    def run(self, **params):
        # Result *always* contains an entry for *every* requested objectId; although
        # that result is None if the object type is unknown or doesn't support ACLs.
        # NOTE: we build in 'expires' to the ACL result because we intend to support
        #       ACLs that expire at some point in the future.
        self.access_check = False
        objects = self._ctx.type_manager.group_ids_by_type(self.object_ids)
        db = self._ctx.db_session()
        array = { }
        for kind in objects:
            if kind in NO_ACL_ENTITIES:
                for object_id in objects[kind]:
                    array[object_id] = None
            elif kind == 'Project':
                query = db.query(ProjectAssignment).\
                    filter(ProjectAssignment.parent_id.in_(objects['Project']))
                acls = query.all()
                for object_id in objects[kind]:
                    array[object_id] = []
                    for acl in acls:
                        if (acl.parent_id == object_id):
                            # Project assignments may-or-may-not be ACLS, depends if they
                            # imply rights.  When we break compatibility with legacy OGo
                            # this is one of the first stupidities we will fix.
                            if acl.rights:
                                array[object_id].append( { 'objectId': acl.object_id,
                                                           'parentObjectId': acl.parent_id,
                                                           'targetObjectId': acl.child_id,
                                                           'operations': acl.rights,
                                                           'expires': None,
                                                           'action': 'allowed' } )
            else:
                query = db.query(ACL).filter(ACL.parent_id.in_(objects[kind]))
                acls = query.all()
                for object_id in objects[kind]:
                    array[object_id] = []
                    for acl in acls:
                        if (acl.parent_id == object_id):
                            array[object_id].append( { 'objectId': acl.object_id,
                                                       'parentObjectId': acl.parent_id,
                                                       'targetObjectId': acl.context_id,
                                                       'operations': acl.permissions,
                                                       'expires': None,
                                                       'action': acl.action } )
        if (self.mode == RETRIEVAL_MODE_SINGLE):
            self._result = array[self.object_ids[0]]
        else:
            self._result = array
