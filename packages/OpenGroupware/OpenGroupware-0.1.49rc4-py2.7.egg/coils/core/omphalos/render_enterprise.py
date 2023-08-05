# Copyright (c) 2009, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from render_object import *
from render_address import *

def render_enterprise(entity, detail, ctx, favorite_ids=None):
    # TODO: Implement
    if (favorite_ids is None):
        ctx.log.error('Omphalos rendering of enterprise recieved a NULL list of favorite ids.')
        favorite_ids = []
    e = { 'associatedCategories': as_string(entity.associated_categories),
          'associatedCompany':    as_string(entity.associated_company),
          'associatedContacts':   as_string(entity.associated_contacts),
          'bank':                 as_string(entity.bank),
          'bankCode':             as_string(entity.bank_code),
          'email':                as_string(entity.email),
          'entityName':           'Enterprise',
          'comment':              as_string(entity.comment),
          'fileAs':               as_string(entity.file_as),
          'imAddress':            as_string(entity.im_address),
          'keywords':             as_string(entity.keywords),
          'name':                 as_string(entity.name),
          'objectId':             as_integer(entity.object_id),
          'isPrivate':            as_integer(entity.is_private),
          'isCustomer':           as_integer(entity.is_customer),
          'sensitivity':          as_integer(entity.sensitivity),
          'ownerObjectId':        as_integer(entity.owner_id),
          'url':                  as_string(entity.URL),
          'version':              as_integer(entity.version) }
    e['_ADDRESSES']  = render_addresses(entity, ctx)
    e['_PHONES'] = render_telephones(entity, ctx)
    if (detail & 8):
        # COMPANY VALUES
        e['_COMPANYVALUES'] = render_company_values(entity, ctx)
    if (detail & 256):
        # CONTACTS
        # The targetObjectId is the enterprise id, how assignments are represented depends on thier
        # context; in a Enterprise entity the targetObjectId is the contact id. The source is the
        # entity being rendered.
        e['_CONTACTS'] = [ ]
        tm = ctx.type_manager
        for assignment in entity.contacts:
            if (tm.get_type(assignment.child_id) == 'Contact'):
                e['_CONTACTS'].append( { 'entityName': 'assignment',
                                         'objectId': as_integer(assignment.object_id),
                                         'sourceEntityName': 'Enterprise',
                                         'sourceObjectId': as_integer(assignment.parent_id),
                                         'targetEntityName': 'Contact',
                                         'targetObjectId': as_integer(assignment.child_id) } )
    if (detail & 1024):
        # PROJECTS
        e['_PROJECTS'] = render_projects(entity, ctx)
    # FLAGS
    flags = []
    rights = ctx.access_manager.access_rights(entity)
    if ('w' in rights): flags.append('WRITE')
    else: flags.append('READONLY')
    if (ctx.account_id == entity.object_id): flags.append('SELF')
    if (entity.is_private == 1): flags.append('PRIVATE')
    if (entity.object_id in favorite_ids):
        flags.append('FAVORITE')
    e['FLAGS'] = flags
    return render_object(e, entity, detail, ctx)
