#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import EntityAccessManager, Team

class TeamAccessManager(EntityAccessManager):
    # TODO: Deal with globally available contacts
    __entity__ = 'Team'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            for right in list('rlv'):
                rights[entity].add(right)
            #TODO: Support team editor role
            if (self._ctx.account_id == 10000):
                rights[entity].add('w') # Modify
                rights[entity].add('d') # Delete
                rights[entity].add('t') # Delete member
        return rights

    @staticmethod
    def List(ctx, properties, contexts=None, mask='r', limit=None, load=True):

        # TODO: Verify the properties are valid; either the Team class
        #        properties of the Team class.  Otherwise this is a
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

        subquery = TeamAccessManager.ListSubquery(ctx, contexts=contexts, mask=mask)

        if (limit is None):
            query = db.query(*properties).\
                    filter(Team.object_id.in_(subquery))
        else:
            query = db.query(*properties).\
                    filter(Team.object_id.in_(subquery)).limit(limit)

        return query.all()

    @staticmethod
    def ListSubquery(ctx, contexts=None, mask='r'):
        if (contexts is None):
            contexts = ctx.context_ids
        db  = ctx.db_session()

        sub_q = db.query(Team.object_id).subquery()

        return sub_q