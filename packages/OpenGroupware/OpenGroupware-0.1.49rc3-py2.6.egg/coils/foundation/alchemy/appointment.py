#
# Copyright (c) 2009, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime       import datetime, date

from sqlalchemy     import Column, String, Integer, ForeignKey, Sequence
from sqlalchemy.orm import relation,backref
from sqlalchemy.ext.associationproxy import association_proxy

from dateutil.tz    import gettz
from base           import Base, KVC
from utcdatetime    import UTCDateTime


class DateInfo(Base, KVC):
    __tablename__       = "date_info"
    __entityName__      = "DateInfo"
    __internalName__    = "DateInfo"
    
    object_id     = Column("date_info_id", Integer, Sequence('key_generator'), primary_key=True)
    parent_id     = Column("date_id", Integer,
                           ForeignKey("date_x.date_id"),
                           nullable=False)
    comment       = Column("comment", String)
    status        = Column("db_status", String(50))

    def __init__(self):
        self.status = 'inserted'

    def update(self, text):
        self.text = text
        self.status = 'updated'
   
    appointment = relation("Appointment", 
                           uselist = False, 
                           backref = backref( "date_x", cascade="all, delete-orphan" ),
                           primaryjoin = ( 'DateInfo.parent_id==Appointment.object_id' ) )    

    
class Appointment(Base, KVC):
    """ An OpenGroupware Appointment object """
    __tablename__        = 'date_x'
    __entityName__       = 'Appointment'
    __internalName__     = 'Date'
    object_id        = Column("date_id", Integer,
                              Sequence('key_generator'),
                              ForeignKey('note.date_id'),
                              ForeignKey('log.object_id'),
                              ForeignKey('object_acl.object_id'),
                              primary_key=True)
    parent_id        = Column("parent_date_id", Integer,
                              ForeignKey('date_x.date_id'),
                              nullable=False)
    version          = Column("object_version", Integer)
    owner_id         = Column("owner_id", Integer,
                              ForeignKey('person.company_id'),
                              nullable=False)
    access_id        = Column("access_team_id", Integer,
                              ForeignKey('team.company_id'),
                              nullable=False)
    start            = Column("start_date", UTCDateTime())
    end              = Column("end_date", UTCDateTime())
    cycle_end        = Column("cycle_end_date", UTCDateTime())
    cycle_type       = Column("type", String(50))
    kind             = Column('apt_type', String(100))
    title            = Column("title", String(255))
    _resource_names  = Column("resource_names", String(255))
    location         = Column("location", String(255))
    keywords         = Column("keywords", String(255))
    status           = Column("db_status", String(50))
    notification     = Column("notification_time", Integer)
    conflict_disable = Column("is_conflict_disabled", Integer)
    write_ids        = Column("write_access_list", String(255))
    importance       = Column("importance", Integer)
    sensitivity      = Column("sensitivity", Integer)
    calendar         = Column("calendar_name", String)
    fb_type          = Column("fbtype", String(50))
    busy_type        = Column("busy_type", Integer)
    contacts         = Column("associated_contacts", String)
    pre_duration     = Column("travel_duration_before", Integer)
    post_duration    = Column("travel_duration_after", Integer)
    caldav_uid       = Column("caldav_uid", String(100))

    def __init__(self):
        self.status            = 'inserted'
        self.conflict_disable  = 0
        self.calendar          = None
        self.version           = 0
        self._specials         = { }
        self._info = DateInfo()
        # TODO: Default free and busy type?

    def __repr__(self):
        return '<Appointment objectId={0} version={1} title="{2}"' \
                           ' ownerId={3} UID="{4}" location="{5}"' \
                           ' start="{6}" end="{7}">'.\
                format(self.object_id,
                       self.version,
                       self.title,
                       self.owner_id,
                       self.caldav_uid,
                       self.location,
                       self.start.strftime('%Y-%m-%d %H:%M %Z'),
                       self.end.strftime('%Y-%m-%d %H:%M %Z'))

    _info = relation("DateInfo", 
                    uselist=False,
                    backref=backref('date_info'),
                    primaryjoin=('DateInfo.parent_id==Appointment.object_id'))    
                    
    comment = association_proxy('_info', 'comment')

    @property
    def ics_mimetype(self):
        return 'text/icalendar'

    def get_resource_names(self):
        result = [ ]
        if (self._resource_names is not None):
            for name in self._resource_names.split(','):
                if (len(name) > 0):
                    result.append(name)
        return result

    def set_resource_names(self, names):
        self._resource_names = ','.join(names)

    def calculate_special_values(self):
        timezone = gettz(self.timezone)
        if not timezone:
            try:
                timezone = '/'.join(self.timezone.split('/')[-2:])
            except:
                timezone = None
            else:
                timezone = gettz(timezone)
        if not timezone:
            raise Exception('Unable to bind timezone "{0}"'.format(self.timezone))
        if (isinstance(self.start, datetime)):
            # This is a normal appointment, not an all-day
            self.isAllDay = 'NO'
            # Record DST status of start-value
            start = self.start.replace(tzinfo=timezone)
            if (timezone.dst(start).total_seconds()):
                self.isStartDST = 'YES'
            else:
                self.isStartDST = 'NO'
            # Record DST status of end-value
            end = self.end.replace(tzinfo=timezone)
            if (timezone.dst(end).total_seconds()):
                self.isEndDST = 'YES'
            else:
                self.isEndDST = 'NO'
        elif (isinstance(self.start, date)):
            self.isAllDay   = 'YES'
            self.isStartDST = 'NO'
            self.isEndDST   = 'NO'

    def set_special_values(self, timezone, allday, start_dst, end_dst):
        self.timezone = timezone
        self.isAllDay = allday
        self.isStartDST = start_dst
        self.isEndDST = end_dst

    @property
    def timezone(self):
        return self.get_special_value('timezone', default='UTC')

    @timezone.setter
    def timezone(self, tzname):
        self.set_special_value('timezone', tzname)

    @property
    def isAllDay(self):
        return self.get_special_value('isAllDay', default='NO')

    @isAllDay.setter
    def isAllDay(self, value):
        self.set_special_value('isAllDay', value)

    @property
    def isStartDST(self):
        return self.get_special_value('isStartDST', default='NO')

    @isStartDST.setter
    def isStartDST(self, value):
        self.set_special_value('isStartDST', value)

    @property
    def isEndDST(self):
        return self.get_special_value('isEndDST', default='NO')

    @isEndDST.setter
    def isEndDST(self, value):
        self.set_special_value('isEndDST', value)

    def get_special_value(self, key, default=None):
        return self._specials.get(key, default)

    def set_special_value(self, key, value):
        if (hasattr(self, '_specials')):
            self._specials[key] = value
        else:
            self._specials = { key: value }

    def get_display_name(self):
        if self.title:
            return self.title[0:127]
        else:
            return str(self.object_id)

    def get_file_name(self):
        return self.caldav_uid if self.caldav_uid else '{0}.ics'.format(self.object_id)


class Resource(Base):
    """ An OpenGroupware scehdular Resource object """
    __tablename__        = 'appointment_resource'
    __entityName__       = 'resource'
    __internalName__     = 'AppointmentResource'
    object_id        = Column("appointment_resource_id", Integer,
                              ForeignKey('log.object_id'),
                              ForeignKey('object_acl.object_id'),
                              primary_key=True)
    version          = Column("object_version", Integer)
    name             = Column("name", String(255), nullable=False)
    category         = Column("category", String(255), nullable=False)
    email            = Column("email", String(255))
    subject          = Column("email_subject", String(255))
    notification     = Column("notification_time", Integer)
    status           = Column("db_status", String(50))

    def __init__(name, category):
        self.name = name
        self.category = category
        self.status = 'inserted'

    def get_display_name(self):
        return '{0}/{1}'.format(self.category, self.name)


class Participant(Base, KVC):
    """ An OpenGroupare Participant object """
    __tablename__       = 'date_company_assignment'
    __entityName__      = 'participant'
    __internalName__    = 'Participant' # Correct?
    object_id           = Column("date_company_assignment_id",
                                Integer,
                                Sequence('key_generator'),
                                primary_key=True)
    appointment_id      = Column("date_id", Integer,
                                 ForeignKey('date_x.date_id'),
                                 nullable=False)
    participant_id      = Column("company_id", Integer,
                                 ForeignKey('person.company_id'),
                                 ForeignKey('team.company_id'),
                                 nullable=False)
    participant_role    = Column("role", String(50))
    participant_status  = Column("partstatus", String(50))
    _db_status          = Column("db_status", String(50))
    comment             = Column("comment", String(255))
    rsvp                = Column("rsvp", Integer)

    def __init__(self):
        self.participant_role = 'REQ-PARTICIPANT'
        self.participant_status = 'NEEDS-ACTION'
        self.comment = ''
        self.rsvp = 0
        self._db_status = 'inserted'

    def __repr__(self):
        return '<Participant objectId="{0}" dateId="{1}" participantId="{2}" role="{3}" status="{4}" rsvp="{5}"/>'.\
            format(self.object_id,
                   self.appointment_id,
                   self.participant_id,
                   self.participant_role,
                   self.participant_status,
                   self.rsvp)

