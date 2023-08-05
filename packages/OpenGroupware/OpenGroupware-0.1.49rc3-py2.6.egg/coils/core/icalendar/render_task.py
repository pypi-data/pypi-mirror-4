#
# Copyright (c) 2009, 2011, 2012
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
import base64, vobject
from StringIO               import StringIO
from datetime               import datetime
from coils.foundation       import Task, ServerDefaultsManager, UniversalTimeZone

def chunk_string(string, delimiter):
    words = []
    for word in string.split(delimiter):
        if (len(word.strip()) > 0):
            words.append(word.strip())
    return words


def as_delimited_string(words, delimiter):
    result = ''
    for word in words:
        if (len(result) > 0):
            result = '{0},{1}'.format(result, word.strip())
        else:
            result = word.strip()
    return result


def render_task(task, todo, ctx, **params):
    
    # UID
    if task.uid:
        todo.add( 'uid' ).value = task.uid
    else:
        todo.add( 'uid' ).value = '{0}@{1}'.format( task.object_id, ctx.cluster_id )

    '''      ; the following are optional,
             ; but MUST NOT occur more than once

             class / completed / created / description / dtstamp /
             dtstart / geo / last-mod / location / organizer /
             percent / priority / recurid / seq / status /
             summary / uid / url /

             ; either 'due' or 'duration' may appear in
             ; a 'todoprop', but 'due' and 'duration'
             ; MUST NOT occur in the same 'todoprop'

             due / duration /

             ; the following are optional,
             ; and MAY occur more than once
             attach / attendee / categories / comment / contact /
             exdate / exrule / rstatus / related / resources /
             rdate / rrule / x-prop
    '''

    # Description / Comment
    if (task.comment is not None):
        # TODO: Sanitize comment
        todo.add('description').value =        task.comment
    else:
        todo.add('description').value =        ''

    todo.add('summary').value = task.name
    todo.add('dtstart').value                = task.start
    todo.add('due').value                    = task.end
    if (task.completed is not None):
        todo.add('completed').value = task.completed
    # Organizer
    # Attendee

    # LAST-MODIFIED
    if task.modified:
        modified = task.modified
    elif task.notes:
        modified = task.notes[0].action_date.astimezone(params['utc_tz'])
    else:
        modified = datetime(1972, 12, 6, 1, 0, 0, tzinfo=UniversalTimeZone())
    # HACK: Sometime OpenGroupware Legacy didn't update the last-modified
    #        value of the task, so we can't really trust it.  We have to
    #        check and see if any of the notes are more current.  This isn't
    #        as bad as it seems since the task.notes is lazy=False in the ORM.
    for action in task.notes:
        if action.action_date.astimezone(params['utc_tz']) > modified:
            modified = action.action_date.astimezone(params['utc_tz'])
    todo.add('last-modified').value = modified

    # ORGANIZER
    owner = ctx.run_command('contact::get', id=task.owner_id)
    if owner:
        cn = None
        email = None
        if ((owner.display_name is not None) and
            (len(owner.display_name) > 0)):
            cn = owner.display_name
        else:
            cn = '{0}, {1}'.format(owner.last_name, owner.first_name)
        # Get email1 from own'er company values (if it exists)
        cv = owner.company_values.get( 'email1', None )
        if cv:
            email = cv.string_value
        # No e-mail found
        if email is None:
            email = 'OGo{0}-UNKNOWN@EXAMPLE.COM'.format(owner.object_id)
        organizer = todo.add('organizer')
        organizer.cn_param = '{0}'.format(cn)
        organizer.cutype_param = 'INDIVIDUAL'
        organizer.value = 'MAILTO:{0}'.format(email)


    # PRIORITY
    # Note: tasks in icalendar have a priority of 0 (undefined) or 1 - 9
    #       where 1 is the highest and nine is the lowest;  OpenGroupware
    #       tasks have a priority of 1 - 5 where 1 is the highest priority
    #       and 5 is the lowest
    if (task.priority == 5):
        todo.add('priority').value = '9'
    elif (task.priority == 4):
        todo.add('priority').value = '8'
    elif (task.priority == 3):
        todo.add('priority').value = '5'
    elif (task.priority == 2):
        todo.add('priority').value = '3'
    elif (task.priority == 1):
        todo.add('priority').value = '1'

    # PERCENT-COMPLETE
    if (task.complete is not None):
        todo.add('percent-complete').value = unicode(task.complete)

    # STATUS
    ''' statvalue  =/ "NEEDS-ACTION"       ;Indicates to-do needs action.
                    / "COMPLETED"           ;Indicates to-do completed.
                    / "IN-PROCESS"          ;Indicates to-do in process of
                    / "CANCELLED"           ;Indicates to-do was cancelled.
        ;Status values for "VTODO".'''
    if (task.state == '00_created'):
        todo.add('status').value    = 'NEEDS-ACTION'
    elif (task.state == '30_archived' or task.state == '25_done'):
        todo.add('status').value    = 'COMPLETED'
    elif (task.state == '20_processing'):
        todo.add('status').value    = 'IN-PROCESS'
    else:
        todo.add('status').value    = 'CANCELLED'

    # URL
    pattern = params['sd'].string_for_default('RSSDefaultItemLinkURL', None)
    if (pattern is not None):
        link = pattern.replace('$objectId', unicode(task.object_id))
        if link:
            todo.add('url').value = link

    # Project (X-COILS-PROJECT)
    if (task.project is not None):
        project = todo.add('x-coils-project')
        project.value = task.project.name
        project.x_coils_project_id_param = unicode(task.project.object_id)
        if (task.project.kind is not None):
            project.x_coils_project_kind_param = task.project.kind

    # Kind (X-COILS-KIND)
    if (task.kind is not None):
        todo.add('x-coils-kind').value = task.kind
        
    todo.add('x-coils-objectid').value = unicode( task.object_id )

    # CATEGORIES
    if task.category:
        # Issue#57
        # Some clients may need to have escaped commas "\,", at least Evolution seems to
        todo.add('categories').value = task.category.split(',')

    # ATTACHMENTS
    if task.attachments:
        for attachment in task.attachments:
            print attachment
            handle = ctx.run_command('attachment::get-handle', attachment=attachment)
            if handle:
                data = handle.read()
                attach = todo.add('attach')
                attach.encoding_param = 'BASE64'
                attach.value_param = 'BINARY'
                if attachment.webdav_uid:
                    attach.x_oracle_filename_param = attachment.webdav_uid
                    attach.x_coils_filename_param = attachment.webdav_uid
                    attach.x_evolution_caldav_attachment_name_param = attachment.webdav_uid
                attach.x_coils_attachment_uuid_param = attachment.uuid
                attach.x_coils_attachment_size_param = str(attachment.size)
                attach.fmttype_param = attachment.mimetype
                attach.value = data
