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
import datetime, re, vobject
from dateutil.tz    import gettz


def take_integer_value(values, key, name, vevent, default=None):
    key = key.replace('-', '_')
    if (hasattr(vevent.key)):
        try:
            values[name] = int(getattr(vevent, key).value)
        except:
            values[name] = default


def take_string_value(values, key, name, vevent, default=None):
    key = key.replace('-', '_')
    if (hasattr(vevent.key)):
        try:
            values[name] = str(getattr(vevent, key).value)
        except:
            values[name] = default


def find_attendee(ctx, email, log):
    if (len(email.strip()) < 6):
        #E-Mail address is impossibly short, don't even bother
        return None
    contacts = ctx.run_command('contact::get', email=email)
    if (len(contacts) == 1):
        contact_id = contacts[0].object_id
        log.debug('Found contact objectId#{0} for e-mail address {1}'.format(contact_id, email))
        return contact_id
    elif (len(contacts) > 1):
        log.warn('Multiple contacts found for e-mail address {0}'.format(email))
    else:
        log.warn('No contact found for e-mail address {0}'.format(email))
    teams = ctx.run_command('team::get', email=email)
    if (teams):
        if (len(teams) > 1):
            log.warn('Multiple teams found for e-mail address {0}'.format(email))
        return teams[0].object_id
    resources = ctx.run_command('resource::get', email=email)
    if (resources):
        if (len(resources) > 1):
            log.warn('Multiple resources found for e-mail address {0}'.format(email))
        return resources[0].object_id
    return None


def parse_attendee(line, ctx, log):
    # Attemdee
    pass

"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PYVOBJECT//NONSGML Version 1//EN
BEGIN:VJOURNAL
DESCRIPTION:
DTSTART:20040430T202842Z
LAST-MODIFIED:20040430T202842Z
SUMMARY:Locking Service Posting
UID:coils://Note/198660
X-COILS-OBJECT-VERSION:None
X-COILS-PROJECT-ID:179420
END:VJOURNAL
END:VCALENDAR
"""

def parse_vjournal(memo, ctx, log, **params):
    # NOTE: vObject is kind enough to give us timezone aware datetimes from
    # start and end elements.  So this utz_tc value is used to convert those
    # TZ aware values to UTC for internal storage.
    utc_tz = gettz('UTC')

    values = {}
    for line in memo.lines():
        if line.name == 'UID':
            keys = line.value.split('/')
            if (keys[0] == 'coils:'):
                if (keys[len(keys) - 1].isdigit()):
                    values['object_id'] = int(keys[len(keys) - 1])
        elif line.name == 'STATUS':
            pass
        elif line.name == 'ATTENDEE':
            pass
        elif line.name == 'SUMMARY':
            values['title'] = line.value
        elif line.name == 'DESCRIPTION':
            values['content'] = line.value
        elif line.name == 'CATEGORIES':
            values['category'] = ','.join(line.value)
        elif line.name == 'ORGANIZER':
            # TODO: This should only be available to someone with the HELPDESK role
            pass
        elif line.name == 'X-COILS-PROJECT-ID':
            if ((len(line.value) == 0) or (line.value == '-')):
                values['project_id'] = None
            elif (line.value.isdigit()):
                # TODO: Verify this is a valid projectId
                values['project_id'] = int(line.value)
            pass
        elif line.name == 'X-COILS-COMPANY-ID':
            if ((len(line.value) == 0) or (line.value == '-')):
                values['company_id'] = None
            elif (line.value.isdigit()):
                # TODO: Verify this is a valid contactId or enterpriseId
                values['company_id'] = int(line.value)
        elif line.name == 'X-COILS-APPOINTMENT-ID':
            if ((len(line.value) == 0) or (line.value == '-')):
                values['date_id'] = None
            elif (line.value.isdigit()):
                # TODO: Verify this is a valid appointmentId
                values['appointment_id'] = int(line.value)
        else:
            # TODO: Save unknown properties as properties so we can put them back
            pass
    if ('object_id' not in values):
        #TODO Can we find other ways to try to find a pre-existing note if the
        #      retarted client dropped the UID attribute [Do not trust clients!]
        pass
    #import pprint
    #print '____begin_values___'
    #pprint.pprint(values)
    #print '____end_values___'
    return [ values ]
