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
from sqlalchemy import *
from coils.core import EntityAccessManager, Process, Message, Route, ACL, ObjectProperty

class MessageAccessManager(EntityAccessManager):
    __entity__ = 'Message'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            rights[entity].add('w') # Modify
            rights[entity].add('d') # Delete
            rights[entity].add('t') # Delete member
            rights[entity].add('l') # List
            rights[entity].add('r') # Read
            rights[entity].add('v') # View
        return rights


class RouteAccessManager(EntityAccessManager):
    __entity__ = 'Route'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            if (entity.owner_id in self.context_ids):
                # Owner has all permissions
                rights[entity].add('w') # Modify
                rights[entity].add('d') # Delete
                rights[entity].add('t') # Delete member
                rights[entity].add('l') # List
                rights[entity].add('r') # Read
                rights[entity].add('v') # View
        return rights

    @staticmethod
    def List(ctx, properties, contexts=None, mask='r', limit=None):
        # TODO: Verify the properties are valid; either the Process class
        #        properties of the Process class.  Otherwise this is a
        #        possible denial-of-service attack vector.

        db  = ctx.db_session()

        # TODO: we shouldn't let a search for a context be exectuted that
        #        that is not part of the current context?  (a search for
        #        processes accessible by a team the current user is not a
        #        member of)
        if contexts is None:
            contexts = ctx.context_ids
        if mask is None:
            mask = 'r'

        routes = db.query(Route.object_id).enable_eagerloads(False).subquery()

        allowed = db.query(ACL.parent_id).\
                  filter(and_(ACL.context_id.in_(contexts),
                               ACL.action=='allowed',
                               ACL.permissions.like('%{0}%'.format(mask)))).\
                  subquery()

        denied = db.query(ACL.parent_id).\
                 filter(and_(ACL.context_id.in_(contexts),
                              ACL.action=='denied',
                              ACL.permissions.like('%{0}%'.format(mask)))).\
                 subquery()

        r_acls = db.query(ACL.parent_id).\
                  filter(and_(ACL.parent_id.in_(routes),
                               ACL.parent_id.in_(allowed),
                               not_(ACL.parent_id.in_(denied)))).distinct()

        if (limit is None):
            enum = db.query(*properties).\
                   filter(or_(Route.owner_id.in_(contexts),
                               Route.object_id.in_(r_acls)))
        else:
            enum = db.query(*properties).\
                   filter(or_(Route.owner_id.in_(contexts),
                               Route.object_id.in_(r_acls))).limit(limit)

        return enum.all()



class ProcessAccessManager(EntityAccessManager):
    ''' Meaning of permissions flags for Process entities
        r = read             [Implies "lv" for Process entities]
        w = write            [Modify; also implies "i"nsert for Process entities]
        l = list             [implied by "r" for Process entities]
        d = delete           [synonymous with t + x]
        a = administer
        k = create           [Not applicable to Process entities]
        t = delete object    [Ability to delete messages from the Process namespace]
        x = delete container [Owner of Process is the owner of the Route?
                              Not implemented.]
        i = insert           [Ability to create messages in the Process namespace.
                              Implied by "w" for Process entities]
        v = view   [Implied by "r" for Process entities]'''

    __entity__ = 'Process'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            if (entity.owner_id in self.context_ids):
                rights[entity].add('a') # Admin
                rights[entity].add('w') # Modify
                rights[entity].add('d') # Delete
                rights[entity].add('t') # Delete member
                rights[entity].add('l') # List
                rights[entity].add('r') # Read
                rights[entity].add('v') # View
        return rights

    @staticmethod
    def List(ctx, properties, contexts=None, mask='r', limit=None, route_group = None):
        # TODO: Add support for filtering by routegroup

        # TODO: Verify the properties are valid; either the Process class
        #        properties of the Process class.  Otherwise this is a
        #        possible denial-of-service attack vector.

        db  = ctx.db_session()

        # TODO: we shouldn't let a search for a context be exectuted that
        #        that is not part of the current context?  (a search for
        #        processes accessible by a team the current user is not a
        #        member of)
        if contexts is None:
            contexts = ctx.context_ids
        if mask is None:
            mask = 'r'

        processes = db.query(Process.object_id).enable_eagerloads(False)
        processes = processes.filter(Process.status != 'archived')
        processes = processes.subquery()

        allowed = db.query(ACL.parent_id).\
                  filter(and_(ACL.context_id.in_(contexts),
                               ACL.action=='allowed',
                               ACL.permissions.like('%{0}%'.format(mask)))).\
                  subquery()

        denied = db.query(ACL.parent_id).\
                 filter(and_(ACL.context_id.in_(contexts),
                              ACL.action=='denied',
                              ACL.permissions.like('%{0}%'.format(mask)))).\
                 subquery()

        r_acls = db.query(ACL.parent_id).\
                  filter(and_(ACL.parent_id.in_(processes),
                               ACL.parent_id.in_(allowed),
                               not_(ACL.parent_id.in_(denied)))).distinct()

        enum = db.query(*properties).\
                 filter(and_(Process.status != 'archived',
                             or_(Process.owner_id.in_(contexts),
                                 Process.object_id.in_(r_acls))))

        if limit:
            enum = enum.limit(limit)

        if route_group:
            enum = enum.join(Route, Route.object_id == Process.route_id)
            enum = enum.join(ObjectProperty, ObjectProperty.parent_id == Route.object_id)
            enum = enum.filter(and_(ObjectProperty.namespace     == 'http://www.opengroupware.us/oie', 
                                              ObjectProperty.name          == 'routeGroup',
                                              ObjectProperty._string_value == route_group ) )

        return enum.all()

'''
Query for the list opertation is the following; this could almost certainly be modified to more
efficiently use joins.

SELECT process.process_id AS process_process_id,
       process.guid AS process_guid,
       process.db_status AS process_db_status,
       process.object_version AS process_object_version,
       process.lastmodified AS process_lastmodified,
       process.route_id AS process_route_id,
       process.priority AS process_priority,
       process.task_id AS process_task_id,
       process.owner_id AS process_owner_id,
       process."state" AS "process_state",
       process.input_message AS process_input_message,
       process.output_message AS process_output_message,
       process.started AS process_started,
       process.parked AS process_parked,
       process.created AS process_created,
       process.completed AS process_completed
FROM process
WHERE process.owner_id IN (...)
   OR process.process_id IN
        (SELECT DISTINCT object_acl.object_id AS object_acl_object_id
           FROM object_acl
          WHERE object_acl.object_id IN (SELECT process.process_id FROM process)
            AND object_acl.object_id IN (SELECT object_acl.object_id
                                           FROM object_acl
                                          WHERE object_acl.auth_id IN (...)
                                            AND object_acl.action = 'allowed'
                                            AND object_acl.permissions LIKE '%r%')
            AND object_acl.object_id NOT IN (SELECT object_acl.object_id
                                               FROM object_acl
                                              WHERE object_acl.auth_id IN (....)
                                                AND object_acl.action = 'denied'
                                                AND object_acl.permissions LIKE '%r%')
'''
