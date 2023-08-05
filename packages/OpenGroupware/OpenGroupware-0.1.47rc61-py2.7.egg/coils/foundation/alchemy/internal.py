#
# Copyright (c) 2009, 2012
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
import uuid
from datetime       import datetime
from time           import time
from sqlalchemy     import *
from base           import *
from utcdatetime    import UTCDateTime


class ObjectInfo(Base):
    """ Object Info Entry """
    __tablename__ = 'obj_info'
    object_id = Column("obj_id", Integer,
                        ForeignKey('person.company_id'),
                        ForeignKey('enterprise.company_id'),
                        ForeignKey('date_x.date_id'),
                        ForeignKey('job.job_id'),
                        ForeignKey('project.project_id'),
                        ForeignKey('doc.document_id'),
                        ForeignKey('note.document_id'),
                        ForeignKey('route.route_id'),
                        ForeignKey('process.process_id'),
                        ForeignKey('company_value.company_value_id'),
                        ForeignKey('collection.collection_id'),
                        ForeignKey('team.company_id'),
                        primary_key=True)
    kind      = Column("obj_type", String(255))
    display_name = Column("display_name", String(128))
    file_name    = Column("file_name", String(128))
    file_size    = Column("file_size", Integer)
    file_type    = Column("file_type", String(128))
    ics_size     = Column("ics_size", Integer)
    ics_type     = Column("ics_type", String(128))
    owner_id     = Column("owner_id", Integer)
    version      = Column("version", Integer)
    created      = Column("created", UTCDateTime)
    modified     = Column("modified", UTCDateTime)
    info_level   = Column("info_level", Integer)


    @staticmethod
    def translate_kind_to_legacy(kind):
        if (kind == "Appointment"):   kind = 'Date'
        elif (kind == "Task"):        kind = 'Job'
        elif (kind == "Contact"):     kind = 'Person'
        elif (kind == "Resource"):    kind = 'AppointmentResource'
        elif (kind == "participant"): kind = 'DateCompanyAssignment'
        elif (kind == "File"):        kind = 'Doc'
        elif (kind == "Document"):    kind = 'Doc'
        return kind

    @staticmethod
    def translate_kind_from_legacy(kind):
        if (kind == 'Doc'): return 'Document'
        elif (kind == 'Job'): return 'Task'
        elif (kind == 'Date'): return 'Appointment'
        elif (kind == 'Person'): return 'Contact'
        elif (kind == 'AppointmentResource'): return 'Resource'
        elif (kind == 'DateCompanyAssignment'): return 'participant'
        return kind

    def __init__(self, object_id, kind, entity=None,
                                        display_name=None,
                                        file_name=None,
                                        file_size=None,
                                        owner_id = None,
                                        version=None):
        self.object_id = object_id
        self.kind = ObjectInfo.translate_kind_to_legacy(kind)
        if entity:
            self.update(entity, file_size=file_size)
        else:
            self.display_name = display_name if display_name else str(self.object_id)
            self.file_name    = file_name if file_name else '{0}.ics'.format(self.object_id)
            self.file_size    = file_size
            self.owner_id     = owner_id
            self.version      = version
            self.info_level   = 1

    def update(self, entity, file_size=None, ics_size=None):
            self.display_name = entity.get_display_name() if hasattr(entity, 'get_display_name') else str(self.object_id)
            self.file_name    = entity.get_file_name() if hasattr(entity, 'get_file_name') else '{0}.ics'.format(self.object_id)
            self.owner_id     = entity.owner_id if hasattr(entity, 'owner_id') else None
            self.version      = entity.version if hasattr(entity, 'version') else 0
            self.created      = entity.created if hasattr(entity, 'created') else self.created
            self.modified     = entity.modified if hasattr(entity, 'modified') else self.modified
            self.ics_type     = entity.ics_mimetype if hasattr(entity, 'ics_mimetype') else None
            self.file_type    = entity.mimetype if hasattr(entity, 'mimetype') else None
            self.kind         = ObjectInfo.translate_kind_to_legacy(entity.__entityName__)
            if file_size:
                self.file_size = file_size
                self.info_level = 6
            else:
                self.info_level = 4
            if ics_size:
                self.ics_size = ics_size

    def __repr__(self):
        return '<ObjectInfo objectId={0} kind="{1}" displayName="{2}" fileName="{3}"' \
                          ' ownerId={4} version={5} mimetype="{6}" icsType="{7}">'.\
                format(self.object_id,
                       self.kind,
                       self.display_name,
                       self.file_name,
                       self.owner_id,
                       self.version,
                       self.file_type,
                       self.ics_type)

class Lock(Base):
    __tablename__       = 'lock'
    __entityName__      = 'lock'
    __internalName__    = 'lock'
    token               = Column('token', String(255), primary_key=True)
    object_id           = Column('object_id', Integer)
    owner_id            = Column('owner_id', Integer)
    granted             = Column('granted', Integer)
    expires             = Column('expires', Integer)
    exclusive           = Column('exclusive', String(1))
    kind                = Column('kind', String(1))
    data                = Column('data', PickleType)
    operations          = Column('operations', String(10))

    def __init__(self, owner_id, object_id, duration, data, delete=True, 
                            write=True, 
                            run=True,
                            exclusive=True):
        self.token      = 'opaquelocktoken:{0}'.format( str( uuid.uuid4( ) ) )
        self.object_id  = object_id
        self.owner_id   = owner_id
        self.granted    = int(datetime.utcnow().strftime('%s'))
        self.expires    = self.granted + duration
        self.data       = data
        self.update_mode(write=write, run=run, exclusive=exclusive, delete=delete)
            
    def update_mode(self, write=True, run=True, exclusive=True, delete=True):
        self.exclusive  = 'N'
        self.operations = ''
        
        if write  or exclusive: self.kind = 'W'
        if write  or exclusive: self.operations += 'w'
        if run    or exclusive: self.operations += 'x'
        if delete or exclusive: self.operations += 'd'
        if exclusive: self.exclusive = 'Y'
        
    @property
    def write(self):
        return 'w' in self.operations
        
    @property
    def run(self):
        return 'x' in self.operations
        
    @property
    def delete(self):
        return 'd' in self.operations
        
    @property
    def is_exclusive(self):
        return self.exclusive == 'Y'
        

    def __repr__(self):
        return '<Lock token="{0}" objectId={1} contextId={2}' \
                   ' granted={3} expires={4} exclusive="{5}">'.\
                format(self.token,
                       self.object_id,
                       self.owner_id,
                       self.granted,
                       self.expires,
                       self.exclusive)


class ObjectLink(Base):
    """ An OpenGroupare Object Link object """
    __tablename__       = 'obj_link'
    __entityName__      = 'objectLink'
    __internalName__    = 'ObjectLink' # Correct?
    object_id           = Column("obj_link_id", Integer,
                                Sequence('key_generator'),
                                primary_key=True)

    kind                = Column("link_type", String(50))
    label               = Column("label", String(255))
    target              = Column("target", String(255))
    source_id           = Column("source_id", Integer)
    source_kind         = Column("source_type", String(50))
    target_id           = Column("target_id", Integer)
    target_kind         = Column("target_type", String(50))

    def __init__(self, source, target, kind, label):
        # TODO: Throw exception if target or source is None
        self.kind = kind
        self.label = label
        self.source_id = source.object_id
        self.source_kind = source.__internalName__
        self.target_id = target.object_id
        self.target_kind = target.__internalName__
        if hasattr(target, 'get_display_name'):
            self.target = target.get_display_name()
        else:
            self.target = unicode(target.object_id)

    def __eq__(self, other):
        if (isinstance(other, int)):
            return self.object_id == other
        elif (isinstance(other, ObjectLink)):
            return (self.kind == other.kind and
                     self.source_id == other.source_id and
                     self.target_id == toher.target_id)
        elif (isinstance(other, dict)):
            return (self.kind == other.get('kind', None) and
                     self.source_id == other.get('source_id', None) and
                     self.target_id == other.get('target_id', None))
        else:
            return False

    def __repr__(self):
        return '<ObjectLink objectId={0} sourceId={1} targetId={2}' \
                   ' kind="{3}" target="{4}" label="{5}">'.\
                format(self.object_id,
                       self.source_id,
                       self.target_id,
                       self.kind,
                       self.target,
                       self.label)


class ACL(Base):
    """ An OpenGroupare Document object """
    __tablename__       = 'object_acl'
    __entityName__      = 'acl'
    __internalName__    = 'ACL' # Correct?
    object_id           = Column("object_acl_id", Integer,
                                Sequence('key_generator'),
                                primary_key=True)
    action              = Column("action", String(10))
    parent_id           = Column("object_id", Integer,
                                 nullable=False)
    context_id          = Column("auth_id", Integer)
    sort_key            = Column('sort_key', Integer)
    permissions         = Column("permissions", String(50))

    def __init__(self, parent_id, context_id, permissions=None, action='allowed'):
        self.parent_id = parent_id
        self.context_id = context_id
        if (permissions is not None):
            self.permissions = permissions.strip().lower()
        else:
            self.permissions = None
        self.action = action
        self.sort_key = 0


    def __repr__(self):
        return '<ACL objectId={0} targetId={1} contextId={2}' \
                   ' action="{3}" sort={4} permissions="{5}">'.\
                format(self.object_id,
                       self.parent_id,
                       self.context_id,
                       self.action,
                       self.sort_key,
                       self.permissions)

class Team(Base, KVC):
    """ An OpenGroupare Team object """
    __tablename__       = 'team'
    __entityName__      = 'Team'
    __internalName__    = 'Team'
    object_id           = Column("company_id",
                                Sequence('key_generator'),
                                ForeignKey('log.object_id'),
                                ForeignKey('object_acl.object_id'),
                                primary_key=True)
    name                = Column("description", String(255))
    is_locality         = Column("is_location_team", Integer)
    version             = Column("object_version", Integer)
    email               = Column("email", String(100))
    owner_id            = Column("owner_id", Integer)

    def get_display_name(self):
        return self.name

    @property
    def ics_mimetype(self):
        return 'text/vcard'

    def __repr__(self):
        return '<Team objectId={0} version={1} name="{2}">'.\
                format(self.object_id,
                       self.version,
                       self.name)


class AuditEntry(Base):
    """ An OpenGroupware Audit Object """
    __tablename__        = 'log'
    __entityName__       = 'logEntry'
    __internalName__     = 'Log' #?
    object_id       = Column("log_id", Integer,
                              Sequence('key_generator'),
                              primary_key=True)
    context_id      = Column("object_id", Integer,
                              nullable=False)
    datetime       = Column("creation_date", UTCDateTime)
    message        = Column("log_text", Text)
    action         = Column("action", String(100))
    actor_id       = Column("account_id", Integer,
                             ForeignKey('person.company_id'))

    def __init__(self):
        self.datetime = datetime.now()

class ProcessLogEntry(Base):
    """ An OpenGroupware Audit Object """
    __tablename__        = 'process_log'
    __entityName__       = 'processLogEntry'
    __internalName__     = 'processLogEntry'
    entry_id       = Column("entry_id", Integer,
                            Sequence('process_log_entry_id_seq'),
                            primary_key=True)
    process_id     = Column("process_id", Integer, nullable=False)
    timestamp      = Column("time_stamp", Numeric, nullable=False)
    message        = Column("message", Text)
    stanza         = Column("stanza", String(32))
    source         = Column("source", String(64))
    uuid           = Column("uuid", String(64))
    category       = Column("category", String(15))

    def __init__(self, source, process_id, message, stanza=None, uuid=None, timestamp=None, category='undefined'):
        if timestamp is None:
            self.timestamp = time()
        else:
            self.timestamp = timestamp
        self.source = source
        self.process_id = process_id
        self.message = message
        self.category = category
        self.uuid = uuid
        self.stanza = stanza


class CTag(Base):
    """ An OpenGroupware CTag Object """
    __tablename__        = 'ctags'
    __entityName__       = 'ctag'
    __internalName__     = 'ctag'
    entity         = Column("entity",String(12), primary_key=True)
    ctag           = Column("ctag", Integer, nullable=False)
