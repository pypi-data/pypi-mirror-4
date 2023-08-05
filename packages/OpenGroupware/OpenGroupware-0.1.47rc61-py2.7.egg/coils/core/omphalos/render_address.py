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
# THE SOFTWARE.
#
from render_object import *

def render_addresses(entity, ctx):
    ''''
        {'city': '',
         'companyObjectId': 10160,
         'country': '',
         'entityName': 'address',
         'name1': '',
         'name2': '',
         'name3': '',
         'objectId': 10210,
         'state': '',
         'street': '',
         'type': 'location',
         'district': '9',
         'zip': ''}
    '''

    if ctx.user_agent_description['omphalos']['associativeLists']:
        result = { }
    else:
        result = [ ]

    if (hasattr(entity, 'addresses')):
        for address in entity.addresses.values():
            tmp = { 'entityName':      'address',
                    'objectId':        address.object_id,
                    'city':            as_string(address.city),
                    'name1':           as_string(address.name1),
                    'name2':           as_string(address.name2),
                    'name3':           as_string(address.name3),
                    'street':          as_string(address.street),
                    'companyObjectId': as_integer(entity.object_id),
                    'state':           as_string(address.province),
                    'country':         as_string(address.country),
                    'type':            as_string(address.kind),
                    'district':        as_string(address.district),
                    'zip':             as_string(address.postal_code) }
            if ctx.user_agent_description['omphalos']['associativeLists']:
                result[address.kind] = tmp
            else:
                result.append(tmp)

    return result


def render_telephones(entity, ctx):
    """""
    {'companyObjectId': 10100,
                      'entityName': 'telephone',
                      'info': '',
                      'number': '',
                      'objectId': 10170,
                      'realNumber': '',
                      'type': '02_tel',
                      'url': ''}
    """
    # TODO: What is the URL field?
    # TODO: Need to populate the, rarely used, "realNumber" attribute

    if ctx.user_agent_description['omphalos']['associativeLists']:
        result = { }
    else:
        result = [ ]

    for telephone in entity.telephones.values():
        tmp = { 'entityName': 'telephone',
                'objectId': telephone.object_id,
                'info': as_string(telephone.info),
                'companyObjectId': as_integer(entity.object_id),
                'number': as_string(telephone.number),
                'realNumber': '',
                'type': telephone.kind,
                'url': '' }
        if ctx.user_agent_description['omphalos']['associativeLists']:
            result[telephone.kind] = tmp
        else:
            result.append(tmp)

    return result


def render_projects(entity, ctx):
    """
        {'entityName': 'assignment',
         'objectId': 11400,
         'sourceEntityName': 'Contact',
         'sourceObjectId': 10100,
         'targetEntityName': 'Project',
         'targetObjectId': 11360}
    """
    result = [ ]
    if (hasattr(entity, 'projects')):
        tm = ctx.type_manager
        for assignment in entity.projects:
            result.append({ 'objectId': assignment.object_id,
                             'sourceEntityName': entity.__entityName__,
                             'sourceObjectId': entity.object_id,
                             'targetEntityName': 'Project',
                             'targetObjectId': assignment.parent_id,
                             'entityName': 'assignment' } )
    return result


# COMPLETE
def render_enterprises(entity, ctx):
    """
        {'entityName': 'assignment',
         'objectId': 11400,
         'sourceEntityName': 'Contact',
         'sourceObjectId': 10100,
         'targetEntityName': 'Project',
         'targetObjectId': 11360}
    """
    result = [ ]
    if (hasattr(entity, 'enterprises')):
        tm = ctx.type_manager
        for assignment in entity.enterprises:
            if (tm.get_type(assignment.parent_id) == 'Enterprise'):
                result.append( { 'entityName': 'assignment',
                                 'objectId': assignment.object_id,
                                 'sourceEntityName': 'Enterprise',
                                 'sourceObjectId': assignment.parent_id,
                                 'targetEntityName': 'Contact',
                                 'targetObjectId': assignment.child_id } )
    return result


# COMPLETE
def render_contacts(entity, ctx):
    """
        {'entityName': 'assignment',
         'objectId': 11400,
         'sourceEntityName': 'Contact',
         'sourceObjectId': 10100,
         'targetEntityName': 'Project',
         'targetObjectId': 11360}
    """
    result = [ ]
    if (hasattr(entity, 'contacts')):
        tm = ctx.type_manager
        for assignment in entity.contacts:
            if (tm.get_type(assignment.child_id) == 'Contact'):
                result.append( { 'objectId': assignment.object_id,
                                 'entityName': 'assignment',
                                 'sourceEntityName': entity.__entityName__,
                                 'sourceObjectId': assignment.parent_id,
                                 'targetEntityName': 'Contact',
                                 'targetObjectId': assignment.child_id } )
    return result


#COMPLETE
def render_company_values(entity, ctx):
    """""
    {'attribute': 'receive_mail',
                     'companyObjectId': 10100,
                     'entityName': 'companyValue',
                     'label': 'Willing To Recieve Mail',
                     'objectId': 4937930,
                     'type': 2,
                     'uid': '',
                     'value': 'YES'}
    """
    values = { }
    for company_value in entity.company_values.values():

        # A UID value makes a company value private: these are rarely used.
        # But an integer NULL is represented in Omphalos as an empty string.
        if (company_value.uid is None):
            uid = ''
        else:
            uid = company_value.uid

        if (company_value.widget == 9):
            # Type 9 indicates that the value is a list, these are stored in the database
            # as a CSV string value.  As a courtest we report these as arrays to clients.
            if (company_value.string_value is None):
                # A NULL is replaced by an emtpy array
                c_value = []
            else:
                c_value = company_value.string_value.split(',')
        else:
            # Non-array (type 9) values
            # A NULL is replaces as an emtpy string
            c_value = as_string(company_value.string_value)

        values[company_value.name] = { 'entityName': 'companyValue',
                                       'objectId': company_value.object_id,
                                       'companyObjectId': entity.object_id,
                                       'label': as_string(company_value.label),
                                       'type': as_integer(company_value.widget),
                                       'uid': uid,
                                       'value': c_value,
                                       'attribute': as_string(company_value.name)}

    sd = ServerDefaultsManager()
    if (isinstance(entity, Enterprise)):
        attr_list = sd.default_as_list('SkyPublicExtendedEnterpriseAttributes')
        attr_list.extend(sd.default_as_list('SkyPrivateExtendedEnterpriseAttributes'))
    elif (isinstance(entity, Contact)):
        attr_list = sd.default_as_list('SkyPublicExtendedPersonAttributes')
        attr_list.extend(sd.default_as_list('SkyPrivateExtendedPersonAttributes'))
    else:
        raise CoilsException('Cannot render company values on a non-company entity.')

    if ctx.user_agent_description['omphalos']['associativeLists']:
        result = { }
    else:
        result = [ ]
        
    for attr in attr_list:
        # A company value that is not defined in the server defaults is supressed from the client
        if (attr['key'] in values):
            # If the company value did not contain a label value but a label value is defined
            # in the server defaults then we inject it into the value returned to the client
            if (len(values[attr['key']]['label']) == 0):
                values[attr['key']]['label'] = attr.get('label', '')
            if ctx.user_agent_description['omphalos']['associativeLists']:
                result[values[attr['key']]['attribute']] = values[attr['key']]
            else:
                result.append(values[attr['key']])

    return result
