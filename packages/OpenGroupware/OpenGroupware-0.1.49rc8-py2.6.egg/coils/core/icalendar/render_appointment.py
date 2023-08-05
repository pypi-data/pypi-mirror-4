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
import datetime, vobject
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


def render_appointment(appointment, event, ctx, log, **params):
    print '__RENDER APPOINTMENT__'
    # The UID of the appointment is the UID assigned by the client, assuming the client applied one (most
    # likely a CalDAV client).  Otherwise a UID is constructed using the object id and the cluster id.
    if appointment.uid:
        uid = appointment.uid
    else:
        uid = '{0}@{1}'.format(appointment.object_id, ctx.cluster_id)
    event.add('uid').value                      = uid
    log.debug( 'AppointmentId#{0} rendered with UID of {1}'.format( appointment.object_id, appointment.uid ) )

    oid = event.add('x-coils-object-id')
    oid.value = str(appointment.object_id)
    oid.cluster_param = ctx.cluster_id

    #
    # ALL DAY?
    #
    all_day = False
    prop = ctx.property_manager.get_property(appointment, 'http://www.opengroupware.us/ics', 'isAllDay')
    if (prop is None):
        # All-day-property not found, use legacy all-day-detection mode
        # TODO: Implement all day event detection (Issue#140)
        event.add('X-MICROSOFT-CDO-ALLDAYEVENT').value = 'FALSE'
        event.add('X-FUNAMBOL-ALLDAY').value = '0'
        all_day = False
    else:
        # Woo Hoo!  Appointment has an isAllDay property
        print 'all day prop is:{0} {1}'.format(prop, prop.get_value())
        if (prop.get_value() == 'YES'):
            event.add('X-MICROSOFT-CDO-ALLDAYEVENT').value = 'TRUE'
            event.add('X-FUNAMBOL-ALLDAY').value = '1'
            print 'rendering in all day mode'
            all_day = True
        else:
            event.add('X-MICROSOFT-CDO-ALLDAYEVENT').value = 'FALSE'
            event.add('X-FUNAMBOL-ALLDAY').value = '0'
            all_day = False

    # Description / Comment
    comment = appointment.comment
    if (comment is not None):
        # TODO: Sanitize comment
        event.add('description').value =        comment
    else:
        event.add('description').value =        ''

    # Title
    event.add('summary').value                  = appointment.title

    # Status  TODO: What is this and what client uses it?
    #               It is in the spec, but is it ever used?
    event.add('status').value                   = 'CONFIRMED'

    # Start / End / Stamp
    # TODO: What is the purpose of DTSTAMP?
    # TODO: We should make sure there is a timezone on DTSTART / DTEND
    event.add('dtstamp').value                  = datetime.datetime.now()
    if all_day:
        log.debug('Appointment being rendered as all-day')
        event.add('dtstart').value                  = appointment.start.date()
        event.add('dtend').value                    = appointment.end.date()
    else:
        log.debug('Appointment being rendered start/end')
        if (appointment.start.tzinfo is None):
            log.debug('Database date/time for appointment start is nieve')
        else:
            log.debug('Database date/time for appointment start has tz of {0}'.format(appointment.start.tzinfo))
        event.add('dtstart').value                  = appointment.start
        if (appointment.end.tzinfo is None):
            log.debug('Database date/time for appointment end is nieve')
        else:
            log.debug('Database date/time for appointment end has tz of {0}'.format(appointment.end.tzinfo))
        event.add('dtend').value                    = appointment.end

    # Location
    if (appointment.location is not None):
        event.add('location').value                 = appointment.location

    event.add('X-MICROSOFT-CDO-INSTTYPE').value = '0'

    event.add('x-coils-read-access').value      = str(appointment.access_id)

    # Appointment 'kind'
    if (appointment.kind is not None):
        event.add('x-coils-appointment-kind').value = appointment.kind
    if (appointment.post_duration is not None):
        event.add('x-coils-post-duration').value = str(appointment.post_duration)
    if (appointment.pre_duration is not None):
        event.add('x-coils-prior-duration').value = str(appointment.pre_duration)
    # Conflicts disabled?
    if (appointment.conflict_disable is not None):
        if (appointment.conflict_disable == 1):
            event.add('x-coils-conflict-disable').value = 'TRUE'
        else:
            event.add('x-coils-conflict-disable').value = 'FALSE'
    else:
        event.add('x-coils-conflict-disable').value = 'FALSE'

    # Categories
    if (appointment.keywords is not None):
        keywords = chunk_string(appointment.keywords, ',')
        if (len(keywords) > 0):
            event.add('categories').value = as_delimited_string(keywords, ',')

    # Class
    if (appointment.sensitivity is not None):
        if (appointment.sensitivity == 0):
            event.add('class').value = 'PUBLIC'
        elif ((appointment.sensitivity == 1) or (appointment.sensitivity == 2)):
            event.add('class').value = 'PRIVATE'
        elif (appointment.sensitivity == 3):
            event.add('class').value = 'CONFIDENTIAL'
        else:
            log.warn('Unknown sensitivity value {0} in appointment {1}'.format(appointment.sensitivity,
                                                                               appointment.object_id))
    # Priority & X-MICROSOFT-CDO-IMPORTANCE
    if (appointment.importance is not None):
        event.add('priority').value = str(appointment.importance)
        if ((appointment.importance > 0) and (appointment.importance < 5)):
            event.add('X-MICROSOFT-CDO-IMPORTANCE').value = "2"
        elif ((appointment.importance > 0) and (appointment.importance < 9)):
            event.add('X-MICROSOFT-CDO-IMPORTANCE').value = "1"
        else:
            event.add('X-MICROSOFT-CDO-IMPORTANCE').value = "0"

    # Transparency (TRANSP) & X-MICROSOFT-CDO-BUSYSTATUS
    if (appointment.fb_type is not None):
        event.add('transp').value = appointment.fb_type
        if (appointment.fb_type == 'TRANSPARENT'):
            event.add('X-MICROSOFT-CDO-BUSYSTATUS').value = 'FREE'
        else:
            event.add('X-MICROSOFT-CDO-BUSYSTATUS').value = 'BUSY'
    elif (appointment.conflict_disable is not None):
        if (appointment.conflict_disable == 1):
            event.add('transp').value = 'TRANSPARENT'
            event.add('X-MICROSOFT-CDO-BUSYSTATUS').value = 'FREE'
        else:
            event.add('transp').value = 'OPAQUE'
            event.add('X-MICROSOFT-CDO-BUSYSTATUS').value = 'BUSY'
    # Related-To
    if (appointment.parent_id is not None):
        # TODO: Is this a spec standard attribute?
        #        Perhaps we should provide a better id?
        event.add('related-to').value = str(appointment.parent_id)

    # TODO: Organizer
    owner = ctx.run_command('contact::get', id=appointment.owner_id)
    if (owner is not None):
        cn = None
        email = None
        if ((owner.display_name is not None) and
            (len(owner.display_name) > 0)):
            cn = owner.display_name
        else:
            cn = '{0}, {1}'.format(owner.last_name, owner.first_name)
        if 'email1' in owner.company_values:
            email = owner.company_values[ 'email1' ].string_value
        if (email is None):
            email = 'OGo{0}-UNKNOWN@EXAMPLE.COM'.format(owner.object_id)
        #organizer = event.add('ORGANIZER')
        #organizer.value = 'CN:{0}:MAILTO={1}'.format(cn, email)
        #organizer.x_coils_organizer_id_param = str(appointment.owner_id)
        cn = None
        email = None
    owner = None



    #
    # ATTENDEE (participants)
    #
    tm = ctx.type_manager
    # Non-Resource participants (from the date_assignment table)
    participants = {}
    for participant in appointment.participants:
        # HACK:Skip NULL participant_ids (this should never happen, but
        #       occasionally one find these in ancient OGo databases)
        if (participant.participant_id is not None):
            object_id = int(participant.participant_id)
            # HACK: We supress duplicate participant entries
            if (object_id not in participants):
                participants[object_id] = participant
    for object_id in participants:
        participant = participants.get(object_id)
        cu = tm.get_type(object_id)
        attendee = event.add('ATTENDEE')
        attendee.x_coils_participant_id_param = str(object_id)
        # CU Type
        if (cu == 'Team'):
            attendee.cutype_param = 'GROUP'
            team = ctx.run_command('team::get', id=object_id)
            if (team is None):
                #TODO: Fix!
                attendee.value= 'CN=OGo{0}:MAILTO=OGo{0}-UNKNOWN@EXAMPLE.COM'.format(str(object_id))
            else:
                #TODO: Fix!
                attendee.value= 'CN={0}:MAILTO={1}'.format(team.name, team.email)
        elif (cu == 'Contact'):
            attendee.cutype_param = 'INDIVIDUAL'
            contact = ctx.run_command('contact::get', id=object_id)
            if (contact is None):
                attendee.cn = 'OGo{0}'.format(str(object_id))
                #attendee.value= 'CN=OGo{0}:MAILTO=OGo{0}-UNKNOWN@EXAMPLE.COM'.format(str(object_id))
                attendee.value = 'MAILTO:OGo{0}-UNKNOWN@EXAMPLE.COM'.format(str(object_id))
            else:
                cn    = None
                email = None
                if 'email1' in contact.company_values:
                    email = contact.company_values[ 'email1' ].string_value                
                if (email is None):
                    email = 'OGo{0}-UNKNOWN@EXAMPLE.COM'.format(str(object_id))
                if ((contact.display_name is None) or
                    (len(contact.display_name.strip()) == 0)):
                    cn = u'{0}, {1}'.format(contact.last_name, contact.first_name)
                else:
                    cn = u'{0}'.format(contact.display_name)
                attendee.cn_param = '{0}'.format(cn)
                attendee.value = 'MAILTO:{0}'.format(email)
        else:
            attendee.cutype_param = 'UNKNOWN'
            attendee.value= 'CN=OGo{0}:MAILTO=OGo{0}-UNKNOWN@EXAMPLE.COM'.format(str(object_id), '')
        # Role
        if (participant.participant_role is None):
            attendee.role_param = 'REQ-PARTICIPANT'
        else:
            attendee.role_param = participant.participant_role
        # Status
        if (participant.participant_status is None):
            attendee.partstat_param = 'NEEDS-ACTION'
        else:
            attendee.partstat_param = participant.participant_status
        # RSVP
        if (participant.rsvp is None):
            attendee.rsvp_param = 'FALSE'
        elif (participant.rsvp > 0):
            attendee.rsvp_param = 'TRUE'
        else:
            attendee.rsvp_param = 'FALSE'
    participants = None
    # Resource participants
    names = appointment.get_resource_names()
    if (len(names) > 0):
        resources = ctx.run_command('resource::get',names=names, access_check=False)
        for resource in resources:
            object_id = resource.object_id
            attendee = event.add('ATTENDEE')
            attendee.x_coils_participant_id_param = str(object_id)
            attendee.x_coils_resource_category_param = resource.category
            attendee.cutype_param = 'RESOURCE'
            attendee.role_param = 'REQ-PARTICIPANT'
            attendee.partstat_param = 'NEEDS-ACTION'
            attendee.rsvp_param = 'FALSE'
            email = None
            if (resource.email is None):
                email = 'OGo{0}-UNKNOWN@EXAMPLE.COM'.format(str(object_id))
            else:
                email = resource.email
            attendee.value= 'CN={0}:MAILTO={1}'.format(resource.name, email)
