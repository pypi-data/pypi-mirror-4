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
from sqlalchemy          import and_, or_, not_
from coils.core          import EntityAccessManager
from coils.foundation    import Collection, ACL

class CollectionAccessManager(EntityAccessManager):
    __entity__ = 'Collection'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            if (entity.owner_id in self.context_ids):
                #aiwmdrf
                rights[entity].add('a') #admin (a)
                rights[entity].add('i') #insert
                rights[entity].add('w') #write
                rights[entity].add('m') #modify
                rights[entity].add('d') #delete
                rights[entity].add('r') # ???
                rights[entity].add('f') # ???
        return rights

    @staticmethod
    def List(ctx, properties, contexts=None, mask='r', limit=None, load=True):

        # TODO: Verify the properties are valid; either the Collection class
        #        properties of the Collection class.  Otherwise this is a
        #        possible denial-of-service attack vector.

        db  = ctx.db_session()

        # TODO: we shouldn't let a search for a context be exectuted that
        #        that is not part of the current context?  (a search for
        #        contacts accessible by a team the current user is not a
        #        member of)
        if contexts is None:
            contexts = ctx.context_ids
        if mask is None:
            mask = 'r'

        subquery = CollectionAccessManager.ListSubquery(ctx, contexts=contexts, mask=mask)

        if (limit is None):
            query = db.query(*properties).\
                    filter(Collection.object_id.in_(subquery))
        else:
            query = db.query(*properties).\
                    filter(Collection.object_id.in_(subquery)).limit(limit)

        return query.all()

    @staticmethod
    def ListSubquery(ctx, contexts=None, mask='r'):
        if (contexts is None):
            contexts = ctx.context_ids
        db  = ctx.db_session()

        has_acl = db.query(ACL.parent_id).subquery()

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

        sub_q = db.query(Collection.object_id).\
                   filter(or_(Collection.owner_id.in_(contexts),
                              (or_(not_(Collection.object_id.in_(has_acl)),
                                   and_(Collection.object_id.in_(allowed),
                                         not_(Collection.object_id.in_(denied))
                                       )
                                   )
                               )
                             )
                         ).\
                   subquery()

        return sub_q


class AttachmentAccessManager(EntityAccessManager):
    __entity__ = 'Attachment'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            if (entity.context_id in self._ctx.context_ids):
                rights[entity].add('w') # Modify
                rights[entity].add('d') # Delete
                rights[entity].add('t') # Delete member
                rights[entity].add('l') # List
                rights[entity].add('r') # Read
                rights[entity].add('v') # View
            elif (entity.related_id is not None):
                pass
        return rights
        
class NoteAccessManager(EntityAccessManager):
    #TODO: Implement!
    __entity__ = 'Note'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        # TODO: Implement
        #        Permissions via assignment
        rights = { }
        for entity in objects:
            rights[entity] = set()
            rights[entity].add('r')
            rights[entity].add('w')
        return rights
                
