# Copyright (c) 2009, 2001 Adam Tauno Williams <awilliam@whitemice.org>
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

#TODO
def render_team_membership(entity, ctx):
    """""
        {'accessRight': '',
         'entityName': 'assignment',
         'info': '',
         'objectId': 479370,
         'sourceEntityName': 'Project',
         'sourceObjectId': 479340,
         'targetEntityName': 'Contact',
         'targetObjectId': 306970 }
    """
    result = [ ]
    if (hasattr(entity, 'teams')):
        tm = ctx.type_manager
        for assignment in entity.teams:
            if (tm.get_type(assignment.parent_id) == 'Team'):
                result.append( { 'entityName': 'assignment',
                                 'objectId': assignment.object_id,
                                 'sourceEntityName': 'Team',
                                 'sourceObjectId': assignment.parent_id,
                                 'targetEntityName': 'Contact',
                                 'targetObjectId': assignment.child_id } )
    return result
    return [ ]

def render_contact(entity, detail, ctx, favorite_ids=None):
    '''
       'assistantName': '',
       'associatedCategories': "''",
       'associatedCompany': 'Morrison Industries',
       'associatedContacts': '',
       'birthDate': <DateTime '19721206T05:00:00' at 819cecc>,
       'comment': '',
       'degree': 'UNIX System Administration',
       'department': '',
       'description': 'Adam Tauno Williams',
       'displayName': '',
       'entityName': 'Contact',
       'fileAs': 'Williams, Adam',
       'firstName': 'Adam',
       'gender': 'male',
       'imAddress': 'adam@m********',
       'isAccount': 1,
       'isPrivate': 0,
       'keywords': ' ',
       'lastName': 'Williams',
       'login': 'adam',
       'managersName': '',
       'middleName': '',
       'objectId': 10100,
       'occupation': '',
       'office': '',
       'birthDate': <DateTime '19721206T00:00:00' at b794688c>,
       'deathDate': <DateTime '21100201T00:00:00' at b79466ec>,
       'birthName': 'Tyler, Rose',
       'birthPlace': 'Outer Mongolia',
       'citizenship': 'AFG',
       'familyStatus': 'awesome',
       'ownerObjectId': 10000,
       'salutation': '03_dear_mr',
       'sensitivity': '',
       'url': '',
       'version': 785
    '''
    
    if favorite_ids is None:
        ctx.log.error('Omphalos rendering of contact recieved a NULL list of favorite ids.')
        favorite_ids = []
        
    c = {
         'entityName':              'Contact',
         'objectId':                entity.object_id,
         'assistantName':           as_string(entity.assistant_name),
         'associatedCategories':    as_string(entity.associated_categories),
         'associatedCompany':       as_string(entity.associated_company),
         'associatedContacts':      as_string(entity.associated_contacts),
         'birthDate':               as_datetime(entity.birth_date),
         'comment':                 as_string(entity.comment),
         'degree':                  as_string(entity.degree),
         'department':              as_string(entity.department),
         'description':             as_string(entity.display_name),
         'displayName':             as_string(entity.display_name),
         'fileAs':                  as_string(entity.file_as),
         'firstName':               as_string(entity.first_name),
         'gender':                  as_string(entity.gender),
         'imAddress':               as_string(entity.im_address),
         'isAccount':               as_integer(entity.is_account),
         'isPrivate':               as_integer(entity.is_private),
         'keywords':                as_string(entity.keywords),
         'lastName':                as_string(entity.last_name),
         'login':                   as_string(entity.login),
         'managersName':            as_string(entity.boss_name),
         'middleName':              as_string(entity.middle_name),
         'occupation':              as_string(entity.occupation),
         'office':                  as_string(entity.office),
         'deathDate':               as_datetime(entity.grave_date),
         'birthName':               as_string(entity.birth_name),
         'birthPlace':              as_string(entity.birth_place),
         'citizenship':             as_string(entity.citizenship),
         'familyStatus':            as_string(entity.family_status),
         'ownerObjectId':           as_integer(entity.owner_id),
         'salutation':              as_string(entity.salutation),
         'sensitivity':             as_string(entity.sensitivity),
         'url':                     as_string(entity.URL),
         'version':                 as_integer(entity.version)
        }

    c['_ADDRESSES']  = render_addresses(entity, ctx)
    c['_PHONES'] = render_telephones(entity, ctx)
    if (detail & 8):
        # COMPANY VALUES
        c['_COMPANYVALUES'] = render_company_values(entity, ctx)
    if (detail & 128):
        # MEMBERSHIP
        c['_MEMBERSHIP'] = render_team_membership(entity, ctx)
    if (detail & 512):
        # ENTERPRISES
        ''' [ { 'entityName': 'assignment',
               'objectId': 12740176,
               'sourceEntityName': 'Contact',
               'sourceObjectId': 12740133,
               'targetEntityName': 'Enterprise',
               'targetObjectId': 12740110 } ] '''
        # The targetObjectId is the contact id, how assignments are represented depends on thier
        # context; in a Contact entity the targetObjectId is the enterprise id. The source is the
        # entity being rendered.
        c['_ENTERPRISES'] = [ ]
        tm = ctx.type_manager
        for assignment in entity.enterprises:
            if (tm.get_type(assignment.parent_id) == 'Enterprise'):
                c['_ENTERPRISES'].append( { 'entityName': 'assignment',
                                            'objectId': as_integer(assignment.object_id),
                                            'sourceEntityName': 'Contact',
                                            'sourceObjectId': as_integer(assignment.child_id),
                                            'targetEntityName': 'Enterprise',
                                            'targetObjectId': as_integer(assignment.parent_id) } )
    if (detail & 1024):
        # PROJECTS
        c['_PROJECTS'] = render_projects(entity, ctx)

    # FLAGS
    flags = []
    rights = ctx.access_manager.access_rights(entity)
    if ('w' in rights): flags.append('WRITE')
    else: flags.append('READONLY')
    if (ctx.account_id == entity.object_id): flags.append('SELF')
    if (entity.is_private == 1): flags.append('PRIVATE')
    # FAVORITE
    if (entity.object_id in favorite_ids):
        flags.append('FAVORITE')
    c['FLAGS'] = flags
    return render_object(c, entity, detail, ctx)
