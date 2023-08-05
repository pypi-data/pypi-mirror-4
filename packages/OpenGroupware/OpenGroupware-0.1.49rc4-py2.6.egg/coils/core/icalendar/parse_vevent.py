# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import datetime, re, uuid, vobject
from dateutil.tz    import gettz
from copy                          import deepcopy
from datetime                      import date, datetime, timedelta


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
        contact_id = None
        log.warn('Multiple contacts found for e-mail address {0}'.format(email))
        for contact in contacts:
            if contact.is_account == 1:
                # TODO: Send user a warning notice
                log.warn('Selected objectId#{0} due to account status.'.format(contact.object_id))
                contact_id = contact.object_id
                break
        else:
            # TODO: Send user a warning notice
            log.warn('Returning arbitrary matching contact.')
            contact_id = contacts[0].object_id
        return contact_id
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
    '''
    {u'attendee': [<ATTENDEE{u'X-COILS-PARTICIPANT-ID': [u'27190'],
                             u'CUTYPE': [u'INDIVIDUAL'],
                             u'ROLE': [u'REQ-PARTICIPANT'],
                             u'PARTSTAT': [u'NEEDS-ACTION'],
                             u'RSVP': [u'TRUE']}
                             CN:SVZ:MAILTO=steve@morrison-ind.com>,
    '''
    participant = {}
    if ('ROLE' in line.params):
        participant['participant_role'] = line.params['ROLE'][0]
    if ('PARTSTAT' in line.params):
        participant['participant_status'] = line.params['PARTSTAT'][0]
    if ('COMMENT' in line.params):
        participant['comment'] = line.params['COMMENT'][0]
    if ('RSVP' in line.params):
        if (line.params['RSVP'][0] in ['YES', 'TRUE', '1', 'yes', 'true']):
            participant['rsvp'] = 1
        else:
            participant['rsvp'] = 0
    if ('X-COILS-PARTICIPANT-ID' in line.params):
        object_id = line.params['X-COILS-PARTICIPANT-ID'][0]
        if (object_id.isdigit()):
            participant['participant_id'] = int(object_id)
    if ('participant_id' not in participant):
        log.debug('No particpant id parameter in ATTENDEE attribute with value "{0}"'.format(line.value))
        # Try to determine participant_id using an embedded OGo Id#
        object_ids = re.findall('=OGo([0-9]*)[-:@]+', line.value)
        for object_id in object_ids:
            if (object_id.isdigit()):
                log.debug('Found OGo#{0} embedded in ATTENDEE'.format(object_id))
                participant['participant_id'] = int(object_ids[0])
                break
        else:
            # Try to determine the participant_id using the mailto
            emails = re.findall('MAILTO[:=]*([A-z@0-9-_+.]*)[;:= ]*', line.value)
            for email in emails:
                 log.debug('** Found email {0} embedded in ATTENDEE'.format(email))
                 participant_id = find_attendee(ctx, email, log)
                 if (participant_id is not None):
                    participant['participant_id'] = participant_id
                    break
            else:
                log.debug('Unable to match ATTENDEE to an existing entity.')
                # Failed to resolve entity for participant
                # TODO: Create a stand-in participant (sadly...)
                # participant['__VALUE__'] = line.value
    if ('participant_id' not in participant):
        return None
    return participant

def parse_vevent(event, ctx, log, calendar=None, starts=[], duration=None, timezone=None, all_day=None):
    # NOTE: vObject is kind enough to give us timezone aware datetimes from
    # start and end elements.  So this utz_tc value is used to convert those
    # TZ aware values to UTC for internal storage.
    utc_tz = gettz('UTC')
    values = { '_PROPERTIES': [] }
    for line in event.lines():
        if line.name == 'UID':
            if (line.value.isdigit()):
                values['object_id'] = int(line.value)
            else:
                values['caldav_uid'] = line.value
        elif line.name == 'STATUS':
            # Our value is always 'CONFIRMED'. This field has no meaning.
            pass
        elif line.name == 'X-COILS-CONFLICT-DISABLE':
            if line.value == 'TRUE':
                values['conflict_disable'] = 1
            else:
                values['conflict_disable'] = 0
        elif line.name == 'ATTENDEE':
            if ('participants' not in values):
                values['participants'] = []
            participant = parse_attendee(line, ctx, log)
            # TODO: Log warning of inability to process ATTENDEE / Participant reference
            # TODO: Notify the user of potential data-loss
            if (participant is not None):
                values['participants'].append(participant)
        elif line.name == 'TRANSP':
            values['fb_type'] = line.value.upper()
        elif line.name == 'DTSTAMP':
            pass
        elif line.name == 'SUMMARY':
            values['title'] = line.value
        elif line.name == 'LOCATION':
            values['location'] = line.value
        elif line.name == 'X-MICROSOFT-CDO-BUSYSTATUS':
            if ('fb_type' in values):
                # If a TRANSP attribute was already used to set the free/busy
                # type then we ignore X-MICROSOFT-CDO-BUSYSTATUS, as TRANSP
                # is a standard attribute.
                pass
            else:
                # A PRIORITY line will override this value
                if (line.value == 'FREE'):
                    values['fb_type'] = 'TRANSPARENT'
                else:
                    values['fb_type'] = 'OPAQUE'
        elif line.name == 'X-COILS-READ-ACCESS':
            object_ids = []
            for object_id in line.value.split(','):
                if (object_id.isdigit()):
                    object_ids.append(int(object_id))
            # TODO: Implement
        elif line.name == 'PRIORITY':
            if line.value.isdigit():
                values['priority'] = int(line.value)
        elif line.name == 'X-MICROSOFT-CDO-IMPORTANCE':
            if 'priority' in values:
                # PRIORITY AND X-MICROSOFT-CDO-IMPORTANCE both do the same
                # thing, so if a PRIORITY value has been processes we just
                # leave it at that.  The value of PRIORITY is a standard.
                pass
            else:
                value = int(line.value)
                # TODO: Implement reverse mapping to priority
                pass
        elif line.name == 'X-MICROSOFT-CDO-INSTTYPE':
            pass
        elif line.name == 'ORGANIZER':
            pass
        elif line.name == 'CLASS':
            sensitivity = line.value.upper().strip()
            if (sensitivity == 'PUBLIC'):
                sensitivity = 0
            elif (sensitivity == 'PRIVATE'):
                sensitivity = 2
            elif (sensitivity == 'CONFIDENTIAL'):
                sensitivity = 3
            else:
                sensitivity = 0
            values['sensitivity'] = sensitivity
        elif line.name == 'X-COILS-APPOINTMENT-KIND':
            values['kind'] = line.value.lower()
        elif line.name == 'X-COILS-OBJECT-ID':
            # TODO: Check the cluster if parameter
            try:
                x = int(line.value.strip())
            except:
                pass
            else:
                values['objectId'] = x
        elif line.name == 'DESCRIPTION':
            values['comment'] = line.value
        elif line.name == 'X-COILS-CONFLICT-DISABLE':
            if line.value == 'TRUE':
                values['conflict_disable'] = 1
            else:
                values['conflict_disable'] = 0
        elif line.name == 'X-COILS-POST-DURATION':
            if (line.value.isdigit()):
                values['post_duration'] = int(line.value)
        elif line.name == 'X-COILS-PRIOR-DURATION':
            if (line.value.isdigit()):
                values['pre_duration'] = int(line.value)
        elif line.name == 'CATEGORIES':
            # TODO: This value is a list of unicode strings, we need it to be a
            #        CSV list; do we escape internal commas?
            # Issue#57
            values['categories'] = ','.join(line.value)
        elif line.name == 'X-COILS-WRITE-ACCESS':
            pass
        elif line.name in ('X-MICROSOFT-CDO-ALLDAYEVENT', 'X-FUNAMBOL-ALLDAY'):
            # These properties are intentially discarded
            pass
        elif line.name == 'ATTACH':
            # TODO: Support the FMTTYPE attribute
            # Get name for attachment, if no name specified generate a UUID to use as the name
            name = None
            # Loop over potential attachment name parameters, these appear to be non-standard
            for name_param in ('X-EVOLUTION-CALDAV-ATTACHMENT-NAME'):
                if name_param in line.params:
                    name = line.params[name_param][0]
                    break
            if name is None:
                name = '{0}.data'.format(uuid.uuid4())
            # Decode the attachment payload
            if 'BINARY' in line.params.get('VALUE', []):
                # Attachment is binary
                if ('BASE64' in line.params.get('ENCODING', [])):
                    pass
            else:
                raise CoilsException('Unsupported iCalendar attachment type encountered')
            parameters =  { }
            for param in line.params:
                parameters[param] = line.params[param]
            log.debug('Found attachment with parameters of: {0}'.format(parameters))
        else:
            if (line.name.startswith('X-')):
                values['_PROPERTIES'].append({ 'namespace': 'http://www.opengroupware.us/ics',
                                               'attribute': line.name.lower(),
                                               'value': line.value } )
            elif (line.name  in ('DTSTART', 'DTEND', 'CREATED', 'LAST-MODIFIED')):
                pass
            else:
                log.debug('VEVENT attribute "{0}" with value of "{1}" discarded'.format(line.name, line.value))
    if ('calendar' is not None):
        values['calendar_name'] = calendar
    if ('object_id' not in values):
        #TODO Can we find other ways to try to find a pre-existing appointment if
        #      the retarted client dropped the UID attribute [Do not trust clients!]
        pass
    result = [ ]
    for start in starts:
        appointment = deepcopy(values)
        if (isinstance(start, datetime)):
            appointment['start'] = start.astimezone(utc_tz)
            appointment['end']   = start.astimezone(utc_tz) + duration
            appointment['timezone'] = timezone
            appointment['isallday'] = 'NO'
        else:
            appointment['start'] = start
            appointment['end']   = start + duration
            appointment['timezone'] = 'UTC'
            appointment['isallday'] = 'YES'

        result.append(appointment)
    return result
