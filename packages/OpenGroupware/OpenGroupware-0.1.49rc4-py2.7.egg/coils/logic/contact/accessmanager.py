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
from coils.foundation    import Contact, ACL
from coils.logic.address import CompanyAccessManager

class ContactAccessManager(CompanyAccessManager):
    ''' Access Evalutation
          1 - All is_account = 1 objects are available to all users
          2 - An owner always has access to a contact, ownership evaluation includes proxy user status.
          3 - An contact that is not is_private == 1 is evaluated for ACLs
              3.1 - An object that is not private and has no ACLs is public
              3.2 - A denied ACL removes permissions over an allowed ACL. '''
    __entity__ = 'Contact'

    def __init__(self, ctx):
        CompanyAccessManager.__init__(self, ctx)

    @staticmethod
    def List(ctx, properties, contexts=None, mask='r', limit=None, load=True):

        # TODO: Verify the properties are valid; either the Contact class
        #        properties of the Contact class.  Otherwise this is a
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

        subquery = ContactAccessManager.ListSubquery(ctx, contexts=contexts, mask=mask)

        if (limit is None):
            query = db.query(*properties).\
                    filter(Contact.object_id.in_(subquery))
        else:
            query = db.query(*properties).\
                    filter(Contact.object_id.in_(subquery)).limit(limit)

        query = query.enable_eagerloads(False)

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
                  enable_eagerloads(False).\
                  subquery()

        denied = db.query(ACL.parent_id).\
                 filter(and_(ACL.context_id.in_(ctx.context_ids),
                             ACL.action=='denied',
                             ACL.permissions.like('%{0}%'.format(mask)))).\
                 enable_eagerloads(False).\
                 subquery()

        sub_q = db.query(Contact.object_id).\
                   filter(or_(Contact.is_account == 1,
                               Contact.owner_id.in_(contexts),
                               and_(or_(Contact.is_private == None, Contact.is_private == 0),
                                    or_(not_(Contact.object_id.in_(has_acl)),
                                        and_(Contact.object_id.in_(allowed),
                                             not_(Contact.object_id.in_(denied))
                                            )
                                       )
                                   )
                               )
                         ).\
                   enable_eagerloads(False).\
                   subquery()

        return sub_q
