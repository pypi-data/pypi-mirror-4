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
from coils.core import EntityAccessManager

class ProjectAccessManager(EntityAccessManager):
    __entity__ = 'Project'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        # TODO: Implement
        #        Permissions via assignment
        rights = { }
        for entity in objects:
            rights[entity] = set()
            if (entity.owner_id in self.context_ids):
                #aiwmdrf
                rights[entity].add('a') #admin (a)
                rights[entity].add('i') #insert
                rights[entity].add('w') #wrire
                rights[entity].add('m') #modify
                rights[entity].add('d') #delete
                rights[entity].add('r') # ???
                rights[entity].add('f') # ???
        return rights

    def asserted_rights(self, object_rights):
        for entity in object_rights.keys():
            rights = object_rights[entity]
            permissions = set(list(self.get_acls('allowed', entity)))
            for right in permissions:
                rights.add(right)
            object_rights[entity] = rights
        return object_rights

    def revoked_rights(self, object_rights):
        # Projects don't support revoked rights
        return object_rights

    def get_acls(self, action, entity):
        rights = set()
        if (action == 'denied'):
            return rights
        else:
            # all project assigneds are forward: allowed
            for acl in entity.assignments:
                if (acl.child_id in self.context_ids):
                    if (acl.rights is not None):
                        permissions = set(list(acl.rights))
                        if (permissions.issubset(rights)):
                            continue
                        for right in permissions:
                            rights.add(right)
            return rights
