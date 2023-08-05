#
# Copyright (c) 2009, 2011, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
#
from datetime   import datetime
from dateutil.tz    import gettz
from coils.core import *

def as_string(value):
    if (value is None):
        return ''
    return value

def as_integer(value):
    if (value is None):
        return 0
    return value

def as_datetime(value):
    if (value is None):
        return ''
    #return xmlrpclib.DateTime(value)
    if isinstance(value, datetime):
        return value
    elif isinstance(value, int):
        return datetime.utcfromtimestamp(value)
    elif isinstance(value, basestring):
        if (len(value) == 10):
            value =  datetime.strptime(x, '%Y-%m-%d').replace(tzinfo=gettz('UTC'))
            value.hour = 0
            value.minute = 0
            return value
        elif (len(value) == 16):
            return datetime.strptime(value, '%Y-%m-%d %H:%M').replace(tzinfo=getz('UTC'))
        else:
            raise CoilsExcpetion('Unable to convert string value to datetime')
    raise CoilsException('Unable to convert value %s to datetime' % str(value))


#COMPLETE
def render_object_links(entity, ctx):
    """ { 'direction': 'from',
          'objectId': '15990',
          'entityName': 'objectLink',
          'targetEntityName': 'Contact',
          'targetObjectId': '10000',
          'label': 'Object Link Label',
          'type': 'generic'} """
    links = []
    tm = ctx.type_manager
    lm = ctx.link_manager
    for link in lm.links_from(entity):
        target_type = tm.get_type(link.target_id)
        links.append({'objectId': link.object_id,
                      'entityName': 'objectLink',
                      'direction': 'from',
                      'targetEntityName': target_type,
                      'targetObjectId': link.target_id,
                      'sourceEntityName': entity.__entityName__,
                      'sourceObjectId': entity.object_id,
                      'label': as_string(link.label),
                      'type': as_string(link.kind) })
    for link in lm.links_to(entity):
        source_type = tm.get_type(link.source_id)
        links.append({'objectId': link.object_id,
                      'entityName': 'objectLink',
                      'direction': 'to',
                      'targetEntityName': entity.__entityName__,
                      'targetObjectId': entity.object_id,
                      'sourceEntityName': source_type,
                      'sourceObjectId': link.source_id,
                      'label': as_string(link.label),
                      'type': as_string(link.kind) })
    return links


#COMPLETE
def render_object_properties(entity, ctx):
    """ {'attribute': 'myIntAttribute',
         'entityName': 'objectProperty',
         'label': '',
         'namespace': 'http://www.whitemiceconsulting.com/properties/ext-attr',
         'parentObjectId': 478560,
         'propertyName': '{http://www.whitemiceconsulting.com/properties/ext-attr}myIntAttribute',
         'type': '',
         'value': 4,
         'valueType': 'int',
         'values': ''} """

    # 2011-11-11 - Added support for associativeLists

    if ctx.user_agent_description['omphalos']['associativeLists']:
        props = { }
    else:
        props = []

    pm = ctx.property_manager
    for prop in pm.get_properties(entity):
        tmp = { 'entityName': 'objectProperty',
                       'attribute': prop.name,
                       'label': prop.label,
                       'namespace': prop.namespace,
                       'parentObjectId': prop.parent_id,
                       'propertyName': '{%s}%s' % (prop.namespace, prop.name),
                       'type': prop.kind,
                       'value': prop.get_value(),
                       'valueType': prop.get_hint(),
                       'values': prop.values }
        if ctx.user_agent_description['omphalos']['associativeLists']:
            props[tmp['propertyName']] = tmp
        else:
            props.append(tmp)

    return props


#COMPLETE
def render_audit_entries(entity, ctx):
    """ { 'action': '00_created',
          'actionDate': <DateTime '20060914T11:13:50' at b79e502c>,
          'actorObjectId': 10120,
          'entityName': 'logEntry',
          'message': 'Company created',
          'objectId': 11050 } """
    result = [ ]
    if (hasattr(entity, 'logs')):
        for log in entity.logs:
            result.append( { 'entityName': 'logEntry',
                             'objectId': log.object_id,
                             'entityObjectId': entity.object_id,
                             'action': log.action,
                             'actionDate': log.datetime,
                             'message': log.message,
                             'actorObjectId': log.actor_id } )
    else:
        ctx.log.warn('%s has no logs attribute' % entity.__entityName__)
    return result


#COMPLETE
def render_acls(entity, ctx):
    """""
    {'entityName': 'acl',
                   'info': '',
                   'operations': 'r',
                   'parentObjectId': 10100,
                   'targetEntityName': 'Team',
                   'targetObjectId': 77210}
    """
    #TODO: Implement
    result = [ ]
    if (hasattr(entity, 'acls')):
        tm = ctx.type_manager
        for acl in entity.acls:
            result.append({'entityName': 'acl',
                           'info': '',
                           'action': acl.action,
                           'parentObjectId': entity.object_id,
                           'targetEntityName': tm.get_type(acl.context_id),
                           'targetObjectId': acl.context_id,
                           'operations': acl.permissions})
    return result


def render_notes(entity, ctx):
    """
    {'creatorObjectId': 10120,
     'projectObjectId': '',
     'objectId': 31350,
     'appointmentObjectId': 28260,
     'projectObjectId': '',
     'title': 'Appointment Note Title',
     'entityName': 'note',
     'ownerObjectId': 10120,
     'content': 'Appointment note text',
     'createdTime': <DateTime u'20060819T23:09:17' at -484d0534>}
    """
    if (isinstance(entity, Task)):
        return None
    if (hasattr(entity, 'notes')):
        result = [ ]
        for note in ctx.run_command('object::get-notes', context=entity):
            result.append({'entityName':          'note',
                           'creatorObjectId':     as_integer(note.creator_id),
                           'projectObjectId':     as_string(note.project_id),
                           'objectId':            as_integer(note.object_id),
                           'appoinmentObjectId':  as_string(note.appointment_id),
                           'title':               as_string(note.title),
                           'ownerObjectId':       as_integer(note.owner_id),
                           'content':             as_string(note.content),
                           'createdTime':         as_datetime(note.created) } )
        return result
    return None


#COMPLETE
def render_object(result, entity, detail, ctx):
    if (detail > 0):
        if (detail & 1):
            # NOTES
            notes = render_notes(entity, ctx)
            if (notes is not None):
                result['_NOTES'] = notes
        if (detail & 2):
            # OBJECT LINKS
            result['_OBJECTLINKS']  = render_object_links(entity, ctx)
        if (detail & 16):
            # OBJECT PROPETIES
            result['_PROPERTIES']  = render_object_properties(entity, ctx)
        if (detail & 32):
            # LOGS
            result['_LOGS']  = render_audit_entries(entity, ctx)
        if (detail & 32768):
            #ACLS
            result['_ACCESS']  = render_acls(entity, ctx)
    return result
