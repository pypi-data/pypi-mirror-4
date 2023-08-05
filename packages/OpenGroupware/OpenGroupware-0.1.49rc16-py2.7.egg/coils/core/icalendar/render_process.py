#
# Copyright (c) 2010, 2011, 2012
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
import datetime, vobject
from StringIO import StringIO
from coils.foundation       import Appointment, Resource


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

def as_safe_datetime(time):
    if (time is None):
        return datetime.datetime.now()
    return time

def draw_properties(ctx, banner=None, entity=None, stream=None):
    stream.write(banner)
    for prop in ctx.property_manager.get_properties(entity):
        stream.write('{{{0}}}{1}\r\n'.format(prop.namespace, prop.name))
        value = prop.get_value()
        if (value is None):
            stream.write('(null)\n')
        else:
            value = unicode(value)
            if (len(value) > 256):
                stream.write('(long)\n')
            else:
                stream.write('{0}\n'.format(value))
        stream.write('\n')
    stream.write('\n')

def render_process(process, event, ctx, **params):
    event.add('uid').value                      = str(process.object_id)

    # Description / Comment
    # Create the comment
    stream = StringIO()
    stream.write('Process objectId#{0} State:{1}\n'.format(process.object_id, process.state))
    if process.route is None:
        stream.write('Route: __adhoc__\n')
    else:
        stream.write('Route: {0} (objectid#{1})\n'.format(process.route.name, process.route.object_id))
        draw_properties(ctx, banner='\n__ROUTE_PROPERTIES___\n', entity=process.route, stream=stream)
    draw_properties(ctx, banner='\n__PROCESS_PROPERTIES___\n', entity=process, stream=stream)
    stream.write('__PROCESS_LOG___\n')
    comment = ctx.run_command('process::get-log', process=process)
    if (comment is None):
        stream.write('(unavailable)')
    else:
        stream.write(comment)
    event.add('description').value = stream.getvalue()
    stream = None

    # Title
    if (process.route is None):
        event.add('summary').value                  = 'Adhoc [Id#{0} {1}]'.format(process.object_id, process.state)
    else:
        event.add('summary').value                  = process.route.name

    event.add('status').value                   = 'CONFIRMED'

    # Start / End / Stamp
    # TODO: What is the purpose of DTSTAMP?
    # TODO: We should make sure there is a timezone on DTSTART / DTEND
    event.add('dtstamp').value                  = datetime.datetime.now()
    if (process.state in ('C', 'F')):
        # Completed / Failed
        if (process.started is None):
            event.add('dtstart').value              = as_safe_datetime(process.created)
        else:
            event.add('dtstart').value              = process.started
        event.add('dtend').value                = as_safe_datetime(process.completed)
    elif (process.state == 'P'):
        # Parked
        if (process.started is None):
            event.add('dtstart').value              = as_safe_datetime(process.created)
        else:
            event.add('dtstart').value              = process.started
        event.add('dtend').value                = as_safe_datetime(process.parked)
    elif (process.state == 'Q'):
        # Parked
        if (process.started is None):
            event.add('dtstart').value              = as_safe_datetime(process.created)
        else:
            event.add('dtstart').value              = process.started
        event.add('dtend').value                = as_safe_datetime(process.created)
    elif (process.state == 'R'):
        if (process.started is None):
            event.add('dtstart').value              = as_safe_datetime(process.created)
        else:
            event.add('dtstart').value              = process.started
        event.add('dtend').value                = datetime.datetime.now()
    else:
        event.add('dtstart').value              = as_safe_datetime(process.created)
        event.add('dtend').value                = as_safe_datetime(process.created)

    # Location
    event.add('location').value                 = ''

    event.add('X-MICROSOFT-CDO-INSTTYPE').value = '0'

    # Appointment 'kind'
    event.add('x-coils-appointment-kind').value = 'oie_process'
    event.add('x-coils-post-duration').value = '0'
    event.add('x-coils-prior-duration').value = '0'
    event.add('x-coils-conflict-disable').value = 'TRUE'

    #event.add('categories').value = as_delimited_string(, ',')
    event.add('class').value = 'PRIVATE'

    # Priority & X-MICROSOFT-CDO-IMPORTANCE
    event.add('priority').value = '1'
    event.add('X-MICROSOFT-CDO-IMPORTANCE').value = "1"

    # Transparency (TRANSP) & X-MICROSOFT-CDO-BUSYSTATUS
    event.add('transp').value = 'TRANSPARENT'
    event.add('X-MICROSOFT-CDO-BUSYSTATUS').value = 'FREE'

    # Related-To
    if (process.route_id is not None):
        event.add('related-to').value = str(process.route_id)

    # TODO: Organizer
    owner = ctx.run_command('contact::get', id=process.owner_id)
    if owner:
        cn = None
        email = None
        if ((owner.display_name is not None) and
            (len(owner.display_name) > 0)):
            cn = owner.display_name
        else:
            cn = '{0}, {1}'.format(owner.last_name, owner.first_name)
        cv = owner.company_values.get( 'email1', None )
        if cv:
            email = cv.string_value
        if (email is None):
            email = 'OGo{0}-UNKNOWN@EXAMPLE.COM'.format(owner.object_id)

    #
    # ATTENDEE (participants)
    #
    attendee = event.add('ATTENDEE')
    attendee.cutype_param = 'INDIVIDUAL'
    contact = ctx.run_command('contact::get', id=process.owner_id)
    if (contact is None):
        attendee.cn = 'OGo{0}'.format(str(process.owner_id))
        attendee.value = 'MAILTO:OGo{0}-UNKNOWN@EXAMPLE.COM'.format(str(process.owner_id))
    else:
        cn    = None
        email = None
        cv = contact.company_values.get( 'email1', None )
        if cv:
            email = cv.string_value
        if email is None:
            email = 'OGo{0}-UNKNOWN@EXAMPLE.COM'.format(str(contact.object_id))
        if ((contact.display_name is None) or
            (len(contact.display_name.strip()) == 0)):
            cn = u'{0}, {1}'.format(contact.last_name, contact.first_name)
        else:
            cn = u'{0}'.format(contact.display_name)
        attendee.cn_param = '{0}'.format(cn)
        attendee.value = 'MAILTO:{0}'.format(email)
        attendee.role_param = 'REQ-PARTICIPANT'
        attendee.partstat_param = 'NEEDS-ACTION'
        attendee.rsvp_param = 'FALSE'
