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
#
from sqlalchemy          import *
from coils.foundation    import Enterprise, ACL
from coils.logic.address import CompanyAccessManager

class EnterpriseAccessManager(CompanyAccessManager):
    __entity__ = 'Enterprise'

    def __init__(self, ctx):
        CompanyAccessManager.__init__(self, ctx)

    @staticmethod
    def List(ctx, properties, contexts=None, mask='r', limit=None):
        db  = ctx.db_session()

        # TODO: we shouldn't let a search for a context be exectuted that
        #        that is not part of the current context?  (a search for
        #        contacts accessible by a team the current user is not a
        #        member of)
        if contexts is None:
            contexts = ctx.context_ids
        if mask is None:
            mask = 'r'

        subquery = EnterpriseAccessManager.ListSubquery(ctx, contexts=contexts, mask=mask)

        if (limit is None):
            query = db.query(*properties).\
                    filter(Enterprise.object_id.in_(subquery))
        else:
            query = db.query(*properties).\
                    filter(Enterprise.object_id.in_(subquery)).limit(limit)

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

        sub_q = db.query(Enterprise.object_id).\
                   filter(or_(Enterprise.owner_id.in_(contexts),
                               and_(or_(Enterprise.is_private == None, Enterprise.is_private == 0),
                                    or_(not_(Enterprise.object_id.in_(has_acl)),
                                        and_(Enterprise.object_id.in_(allowed),
                                             not_(Enterprise.object_id.in_(denied))
                                            )
                                       )
                                   )
                               )
                         ).\
                   subquery()

        return sub_q