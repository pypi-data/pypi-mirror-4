#
# Copyright (c) 2009, 2012
# Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime                    import datetime

from sqlalchemy                      import Column, DateTime, Integer, ForeignKey, Sequence, String, case
from sqlalchemy.orm                  import relation,backref,column_property
from sqlalchemy.ext.associationproxy import association_proxy

from utcdatetime                 import UTCDateTime
from base                        import Base, KVC
from coils.foundation.mimetypes  import *



class Note(Base, KVC):
    """ An OpenGroupare Note object """
    __tablename__       = 'note'
    __entityName__      = 'note'
    __internalName__    = 'Note' # Correct?
    object_id           = Column("document_id",
                                Integer,
                                Sequence('key_generator'),
                                primary_key=True)
    appointment_id      = Column("date_id", Integer,
                                 ForeignKey('date_x.date_id'),
                                 nullable=True)
    project_id          = Column("project_id", Integer,
                                 ForeignKey('project.project_id'),
                                 nullable=True)
    company_id          = Column("company_id", Integer,
                                 ForeignKey('person.company_id'),
                                 ForeignKey('enterprise.company_id'),
                                 nullable=True)
    is_note             = Column("is_note", Integer, default=1)
    version             = Column("object_version", Integer)
    title               = Column("title", String(255))
    abstract            = Column("abstract", String(255))
    kind                = Column("file_type", String(255))
    status              = Column("db_status", String(50), default='inserted')
    file_size           = Column("file_size", Integer)
    creator_id          = Column("first_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=True)
    created             = Column("creation_date", UTCDateTime())
    owner_id            = Column("current_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=True)
    modified            = Column("lastmodified_date", UTCDateTime())
    categories          = Column('categories', String(255))
    caldav_uid          = Column('caldav_uid', String(128))

    def get_mimetype(self):
        return 'text/plain'

    @property
    def mimetype(self):
        return 'text/plain'

    @property
    def ics_mimetype(self):
        return 'calendar/ics'

    def get_path(self):
        return 'documents/{0}.{1}'.format(self.object_id, self.kind)

    def get_display_name(self):
        if self.title:
            return self.title.strip()
        return 'noteId#{0}'.format(self.object_id)

    def get_file_name(self):
        return '{0}.txt'.format(self.object_id)

    def __repr__(self):
        return '<Note objectId="{0}" version="{1}" title="{2}"' \
                    ' kind="{3}" projectId="{4}" ownerId="{5}"' \
                    ' appointmentId="{6}" companyId="{7}"' \
                    ' created="{8}" modified="{9}"' \
                    ' size="{10}"/>'.\
                format(self.object_id,
                       self.version,
                       self.title,
                       self.kind,
                       self.project_id,
                       self.owner_id,
                       self.appointment_id,
                       self.company_id,
                       self.created.strftime('%Y%m%dT%H:%M') if self.created else '',
                       self.modified.strftime('%Y%m%dT%H:%M') if self.modified else '',
                       self.file_size)

    @property
    def content(self):
        if hasattr(self, '_content'):
            return self._content
        else:
            raise Exception('Note content not initialized.')

    @content.setter
    def content(self, value):
        #print 'setting note content = {0}'.format(value)
        setattr(self, '_content', value)

        
class DocumentEditing(Base):
    __tablename__       = 'document_editing'
    __entityName__      = 'documentVersion'
    __internalName__    = 'DocumentVersion' # Correct?
    object_id           = Column("document_editing_id",
                                Integer,
                                Sequence('key_generator'),
                                primary_key=True)
    version             = Column("version", Integer, nullable = False)
    document_id         = Column("document_id", Integer, nullable = False)
    owner_id            = Column("current_owner", Integer, nullable = False)
    title               = Column("title", String(255))
    abstract            = Column("abstract", String(255))
    extension           = Column("file_type", String(255))
    file_size           = Column("file_size", Integer)
    edition             = Column("version", Integer)
    dirty               = Column("is_attach_changed", Integer)
    #checkout_date       = Column("", Integer) -- Timestamp
    state               = Column("status", String(50))
    status              = Column("db_status", String(50))
    contact             = Column("contact", String(255))


class DocumentVersion(Base):
    __tablename__       = 'document_version'
    __entityName__      = 'documentVersion'
    __internalName__    = 'documentVersion' # Correct?

    object_id           = Column("document_version_id",
                                Integer,
                                Sequence('key_generator'),
                                primary_key=True)

    document_id         = Column("document_id", Integer,
                                 ForeignKey('doc.document_id'),
                                 nullable=True)

    owner_id            = Column("last_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=False)

    version             = Column("version", Integer, nullable = False)
    packed              = Column("is_packed", Integer)
    created             = Column("creation_date", DateTime())
    name                = Column("title", String(255))
    abstract            = Column("abstract", String(255))
    archived            = Column("archive_date", DateTime())
    change_text         = Column("change_text", String)
    file_size           = Column("file_size", Integer)
    extension           = Column("file_type", String(255), nullable = False)
    checksum            = Column("checksum",  String(128))
    status              = Column("db_status", String(50))

    def __init__(self, document, change_text=None, checksum=None):
        self.status      = 'inserted'
        self.document_id = document.object_id
        self.owner_id    = document.owner_id
        self.created     = document.created
        self.version     = document.version_count + 1
        self.name        = document.name
        self.abstract    = document.abstract
        self.extension   = document.extension
        self.file_size   = document.file_size
        self.archived    = datetime.now()
        self.change_text = change_text
        self.packed      = 0
        self.checksum    = checksum
        document.version_count += 1

    def set_checksum(self, checksum):
        self.checksum = checksum

    def set_file_size(self, file_size):
        self.file_size = file_size

    def __repr__(self):
        return '<DocumentVersion objectId="{0}"' \
                                ' version="{1}"' \
                                ' documentId="{2}"' \
                                ' name="{3}"' \
                                ' extension="{4}"' \
                                ' owner="{5}"' \
                                ' created="{6}"'\
                                ' packed="{7}"' \
                                ' size="{8}"' \
                                ' checksum="{9}"/>'. \
                format(self.object_id,
                       self.version,
                       self.document_id,
                       self.name,
                       self.extension,
                       self.owner_id,
                       self.created.strftime('%Y%m%dT%H:%M'),
                       self.packed,
                       self.file_size,
                       self.checksum)

    def get_mimetype(self):
        if (self.extension is None):
            return 'application/octet-stream'
        return COILS_MIMETYPEMAP.get(self.extension, 'application/octet-stream')

    document = relation("Document", 
                        uselist = False, 
                        backref = backref( "document", cascade="all, delete-orphan" ),
                        primaryjoin = ('DocumentVersion.document_id==Document.object_id') )  


class _Doc(Base):
    """ An OpenGroupare Document object """
    __tablename__       = 'doc'
    __internalName__    = 'Doc' 
    
    object_id           = Column("document_id",
                                Integer,
                                Sequence('key_generator'),
                                ForeignKey('log.object_id'),
                                ForeignKey('object_acl.object_id'),
                                primary_key=True)
    appointment_id      = Column("date_id", Integer,

                       ForeignKey('date_x.date_id'),
                                 nullable=True)
    project_id          = Column("project_id", Integer,
                                 ForeignKey('project.project_id'),
                                 nullable=True)
    company_id          = Column("company_id", Integer,
                                 ForeignKey('person.company_id'),
                                 ForeignKey('enterprise.company_id'),
                                 nullable=True)
    folder_id           = Column("parent_document_id", Integer,
                                 ForeignKey('doc.document_id'),
                                 nullable=True)
    version             = Column("object_version", Integer)
    version_count       = Column("version_count", Integer, default=0)
    abstract            = Column("abstract", String(255))
    status              = Column("db_status", String(50))
    state               = Column("status", String(50))
    name                = Column("title", String(255))
    creator_id          = Column("first_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=False)
    created             = Column("creation_date", DateTime())
    owner_id            = Column("current_owner_id", Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=False)
    modified            = Column("lastmodified_date", DateTime())
    extension           = Column("file_type", String(255), nullable = False)
    file_size           = Column("file_size", Integer)

    _is_folder          = Column("is_folder", Integer)
    _is_link            = Column("is_object_link", Integer)
    _entity_name        = column_property( case( [ (_is_folder==1, "folder") ,
                                                   (_is_link==1, "link"), ],
                                                 else_="document" ) )
    
    __mapper_args__     = { 'polymorphic_on': _entity_name }

    def __init__(self):
        self.version = 1
        self.version_count = 0
        self._is_link = 0

    def get_mimetype(self):
        if ((self._is_folder == 1) or (self.extension is None)):
            return None
        return COILS_MIMETYPEMAP.get(self.extension, 'application/octet-stream')


class Document(_Doc, KVC):
    __entityName__  = 'Document'
    __mapper_args__ = {'polymorphic_identity': 'document'}

    _version = relation("DocumentVersion", 
                    uselist=False,
                    backref=backref('document_version'),
                    primaryjoin=('and_(DocumentVersion.document_id==Document.object_id, DocumentVersion.version==Document.version_count)'))    
                    
    checksum = association_proxy('_version', 'checksum')

    def __init__(self):
        self._is_folder = 0

    def skyfs_path_to_version(self, version):
        #
        # TODO: This is *seriously* deprecated and should *NEVER* be used
        #       Replace this with a raise Exception in order to find
        #       anything anywhere that uses this ugly thing
        #
        if (self.project_id is None):
            raise Exception('Attempt to get SKYfs path for a non-project document')
        for edition in self.versions:
            if edition.version == version:
                version = edition
                break
        else:
            raise Exception('No such version as {0} for documentId#{1}'.format(version, self.object_id))
        return '/documents/{0}/{1}/{2}.{3}'.format(self.project_id,
                                                   (1000 * ( version.object_id / 1000)),
                                                   version.object_id,
                                                   version.extension)

    def create_version(self, text):
        self.version = self.version + 1
        return DocumentVersion(self, text)

    def get_display_name(self):
        if (self.extension is None):
            return self.name
        else:
            return '{0}.{1}'.format(self.name, self.extension)

    def get_file_name(self):
        return self.get_display_name()

    def __repr__(self):
        return '<Document objectId="{0}" version="{1}" name="{2}"' \
                        ' extension="{3}" project="{4}" owner="{5}" ' \
                        ' folder="{6}" created="{7}" modified="{8}"' \
                        ' size="{9}" checksum="{10}" revisions="{11}"/>'.\
                format(self.object_id, 
                       self.version, 
                       self.name,
                       self.extension,
                       self.project_id, 
                       self.owner_id, 
                       self.folder_id,
                       self.created.strftime('%Y%m%dT%H:%M'),
                       self.modified.strftime('%Y%m%dT%H:%M'),
                       self.file_size,
                       self.checksum,
                       self.version_count)

    def set_file_size(self, file_size):
        self.file_size = file_size

    @property
    def mimetype(self):
        return self.get_mimetype()

    def get_mimetype(self, type_map=None):
        if (self.extension is None):
            return 'application/octet-stream'
        elif (type_map is not None):
            return type_map.get(self.extension.lower(), 'application/octet-stream')
        else:
            return COILS_MIMETYPEMAP.get(self.extension.lower(), 'application/octet-stream')


class Folder(_Doc, KVC):
    __entityName__  = 'Folder'
    __mapper_args__ = {'polymorphic_identity': 'folder'}
    
    def __init__(self):
        _Doc.__init__(self)
        self.status = 'inserted'
        self.version = 0
        self._is_folder = 1

    def get_display_name(self):
        return self.name

    def get_file_name(self):
        return self.get_display_name()

    def __repr__(self):
        return '<Folder objectId={0} version={1} name="{2}"' \
                        ' project={3} owner={4} folder="{5}"/>'. \
                format(self.object_id, self.version, self.name,
                       self.project_id, self.owner_id, self.folder_id)

