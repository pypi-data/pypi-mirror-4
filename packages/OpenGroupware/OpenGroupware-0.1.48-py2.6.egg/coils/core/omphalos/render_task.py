#
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
import time
from coils.foundation import OGO_ROLE_HELPDESK
from render_object import *

TASK_ACTIONS = [ { 'state':  set( ['00_created', '20_processing', ] ),
                   'rights': set( [ 'w' ] ),
                   'flags':  set( ['EXECUTOR', 'OWNER', 'CANDIDATE', ] ),
                   'flag':   'DONE', },
                 { 'state':  set( [ '00_created', '20_processing', '25_done' ] ),
                   'flags':  set( [ 'OWNER' ] ),
                   'rights': set( [ 'w' ] ),
                   'flag':   'ARCHIVE', } ,
                 { 'state':  set( [ '25_done', '30_archived', ] ),
                   'flags':  set( [ 'EXECUTOR', 'OWNER', 'CANDIDATE', ] ),
                   'rights': set( [ 'w' ] ),
                   'flag':   'REACTIVATE', } ,
                 { 'state':  set( [ '02_rejected', ] ),
                   'flags':  set( [ 'OWNER', 'HELPDESK' ] ),
                   'rights': set( [ 'w' ] ),
                   'flag':   'REACTIVATE', } ,
                 { 'state':  set( [ '00_created', ] ),
                   'rights': set( [ 'w' ] ),
                   'flags':  set( ['EXECUTOR', 'CANDIDATE', ] ),
                   'flag':   'ACCEPT', } ,
                 { 'state':  set( [ '00_created', ] ),
                   'rights': set( [ 'w' ] ),
                   'flags':  set( ['EXECUTOR', 'CANDIDATE', ] ),
                   'flag':   'REJECT', } , 
                 { 'state':  set( [ '20_processing', ] ),
                   'rights': set( [ 'w' ] ),
                   'flags':  set( ['EXECUTOR', ] ),
                   'flag':   'REJECT', } , ] 

def render_task_notations(entity):
    """
        {'comment': 'COMMENT COMMENT COMMENT',
         'actionDate': <DateTime u'20061205T11:58:44' at -484cd194>,
         'objectId': 38330,
         'entityName': 'taskNotation',
         'taskStatus': '00_created',
         'taskObjectId': 38320,
         'action': '00_created',
         'actorObjectId': 10120}
    """
    result = [ ]
    for notation in entity.notes:
        result.append({ 'entityName': 'taskNotation',
                        'objectId':      as_integer(notation.object_id),
                        'comment':       as_string(notation.comment),
                        'taskStatus':    as_string(notation.task_status),
                        'taskObjectId':  as_integer(notation.task_id),
                        'actionDate':    as_datetime(notation.action_date),
                        'action':        as_string(notation.action),
                        'actorObjectId': as_integer(notation.actor_id) })
    return result

def render_task(entity, detail, ctx):
    # TODO: Implement
    """
    {'comment': 'COMMENT COMMENT COMMENT',
     'sensitivity': 2,
     'percentComplete': 40,
     'keywords': 'ZOGI',
     'category': '',
     'completionDate': '',
     'end': <DateTime '20070125T00:00:00' at 815416c>,
     '_OBJECTLINKS': [{'direction': 'from',
                       'objectId': '15990',
                       'entityName': 'objectLink',
                       'targetEntityName': 'Contact',
                       'targetObjectId': '10000',
                       'label': 'Object Link Label',
                       'type': 'generic'}],
     'objectId': 476660,
     'priority': 2,
     'start': <DateTime '20061231T00:00:00' at 815408c>,
     'version': 2,
     'accountingInfo': 'Accounting Info',
     '_PROPERTIES': [],
     'executantObjectId': 10160,
     'entityName': 'Task',
     'status': '20_processing',
     'creatorObjectId': 10160,
     'ownerObjectId': 54720,
     'associatedContacts': '',
     'associatedCompanies': '',
     'timerDate': '',
     'kilometers': '34',
     'totalWork': 75,
     '_NOTES': [],
     'isTeamJob': 0,
     'parentTaskObjectId': 11409747,
     'kind': '',
     'name': 'Updated ZOGI Task 5',
     'lastModified': '',
     'objectProjectId': '',
     'actualWork': 23,
     'graph': {'12339323': {'12677171': {},
                            '12710721': {},
                            '12710725': {},
                            '12736451': {},
                            '12739574': {},
                            '12751507': {'11409747': {'476660': {}},
                                         '4560420': {}},
                            '12757951': {}}},
     'notify': 1}
    """
    executor_type = ctx.type_manager.get_type(entity.executor_id)
    if (executor_type == 'Team'):
        is_team_job = 1
    else:
        is_team_job = 0
    task = { 'entityName':          'Task',
             'objectId':            entity.object_id,
             'version':             as_integer(entity.version),
             'comment':             as_string(entity.comment),
             'sensitivity':         as_integer(entity.sensitivity),
             'percentComplete':     as_integer(entity.complete),
             'keywords':            as_string(entity.keywords),
             'category':            as_string(entity.category),
             'completionDate':      as_datetime(entity.completed),
             'end':                 as_datetime(entity.end),
             'start':               as_datetime(entity.start),
             'priority':            as_integer(entity.priority),
             'accountingInfo':      as_string(entity.accounting),
             'executantObjectId':   as_integer(entity.executor_id),
             'status':              as_string(entity.state),
             'creatorObjectId':     as_integer(entity.creator_id),
             'ownerObjectId':       as_integer(entity.owner_id),
             'associatedContacts':  as_string(entity.associated_contacts),
             'associatedCompanies': as_string(entity.associated_companies),
             'timerDate':           as_datetime(entity.timer),
             'kilometers':          as_integer(entity.travel),
             'totalWork':           as_integer(entity.total),
             'isTeamJob':           is_team_job,
             'parentTaskObjectId':  as_integer(entity.parent_id),
             'kind':                as_string(entity.kind),
             'name':                as_string(entity.name),
             'objectProjectId':     as_integer(entity.project_id),
             'actualWork':          as_integer(entity.actual)
           }

    if entity.modified:
        task['lastModified'] = int(time.mktime(entity.modified.timetuple()))
    else:
        task['lastModified'] = ''

    # HACK: sometimes we encounter oddly high/low task priorities, the range is 1 - 5
    #       this probably results from someone manually screwing around in their DB
    if task['priority'] < 1:
        task['priority'] = 1
    elif task['priority'] > 5:
        task['priority'] = 5

    # Set extra projectName / projectNumber attributes
    # NOTE: This is an extension beyond the original zOGI properties provided for a task,
    #       but include this can same the client a fair amount of extra work maintaining
    #       a project list when this may be the only attribute of project-ness they care
    #       about.
    if entity.project_id:
        project = entity.project
        if project:
            task['projectName'] = project.name
            task['projectNumber'] = project.number

    # Graph
    if detail & 128:
        task['graph'] = ctx.run_command('task::get-graph', object=entity)

    # Annotations
    if detail & 1:
        # TASK HISTORY
        task['_NOTES'] = render_task_notations(entity)

    # Flags
    flags = [ ]
    rights = ctx.access_manager.access_rights(entity)
    if ctx.has_role( OGO_ROLE_HELPDESK ): flags.append( 'HELPDESK' )
    if ('w' in rights): flags.append('WRITE')
    else: flags.append('READONLY')
    if ('r' in rights): flags.append('READ')
    else: flags.append('VISIBLE')
    if ('d' in rights): flags.append('DELETE')
    if (ctx.account_id == entity.owner_id): flags.append('OWNER')
    if (ctx.account_id == entity.creator_id): flags.append('CREATOR')
    if (ctx.account_id == entity.executor_id): flags.append('EXECUTOR')
    elif (entity.executor_id in ctx.context_ids): flags.append('CANDIDATE')
    if (entity.state in ('00_created', '20_processing')):
        now = ctx.get_utctime()
        if (entity.start > now): flags.append('UPCOMING')
        elif (entity.end < now): flags.append('OVERDUE')
    for action in TASK_ACTIONS:
        if ( action[ 'rights' ].intersection( rights ) and 
             action[ 'flags' ].intersection( flags ) and
             entity.state in action[ 'state' ] ):
            if action[ 'flag' ] not in flags:
                flags.append( action[ 'flag' ] )

    # FAVORITE
    #if (entity.object_id in favorite_ids):
    #    flags.append('FAVORITE')

    task['FLAGS'] = flags
    return render_object(task, entity, detail, ctx)
