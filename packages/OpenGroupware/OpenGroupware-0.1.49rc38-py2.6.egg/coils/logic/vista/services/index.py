#
# Copyright (c) 2011, 2012, 2013
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
#
import uuid, shutil, traceback
from datetime            import datetime, timedelta
from coils.core          import *
from orm                 import SearchVector
from StringIO            import StringIO
from sqlalchemy          import func
from coils.foundation.api.pypdf import PdfFileReader, EncryptedPDFException, PdfReadError
from edition             import INDEXER_EDITION

def normalize_string(value):
    if value:
        if isinstance(value, list):
            return ' '.join(value).lower()
        elif isinstance(value, basestring):
            return ' {0} '.format(value.lower().strip())
    return ''

def normalize_datetime(value):
    if value:
        return ' {0} '.format(value.strftime('%Y-%m-%d %H:%M'))
    else:
        return ''

def parse_keywords(value, delimiter = ' '):
    keywords = [ ]
    if value:
        if isinstance(keywords, basestring):
            keywords = [ x.strip().lower()
                        for x in value.split(delimiter)
                        if len(x) < 128 ]
        elif isinstance(value, list):
            keywords = [ x.strip().lower()
                         for x in value
                         if len(x) < 128 ]
    return keywords

class IndexService (ThreadedService):
    __service__ = 'coils.vista.index'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)

    def setup(self, silent=True):
        ThreadedService.setup( self, silent=silent )
        self._broker.subscribe( '{0}.{1}'.format( self.__service__, uuid.uuid4().hex ),
                                self.receive_message,
                                expiration=900000,
                                queue_type='fanout',
                                durable=False,
                                exchange_name='OpenGroupware_Coils_Notify' )

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext( { }, broker=self._broker )
        self._floor = None

    #
    # Message Handlers
    #

    def do_log_scan(self, parameter, packet):

        if self._floor:
            floor = self._floor
        else:
            floor = datetime.now( ) - timedelta( hours=72 )
            floor = floor.replace( tzinfo=UniversalTimeZone( ) )

        db = self._ctx.db_session( )
        query = db.query( AuditEntry.context_id, func.max( AuditEntry.datetime ) ).\
                          filter( AuditEntry.datetime > floor ).group_by( AuditEntry.context_id )
        for record in query.all( ):
            object_id, event_time = record
            if event_time > floor:
                floor = event_time
            self._ctx.send( None, 'coils.vista.index/index:{0}'.format( object_id ), { } )
        self._floor = floor

    def do_vacuum(self, parameter, packet):
        db = self._ctx.db_session( )
        query = db.query( SearchVector.object_id ).\
                   outerjoin( ObjectInfo, ObjectInfo.object_id == SearchVector.object_id ).\
                   filter( ObjectInfo.object_id == None )
        result = query.all( )
        count = len( result )
        self.log.debug( 'Purging {0} defunct search vectors.'.format( count ) )
        while result:
            chunk = result[ : 100 if len( result ) > 100 else len( result ) ]
            del result[ : len( chunk )]
            db.query( SearchVector ).filter( SearchVector.object_id.in_( chunk ) ).delete( synchronize_session=False )
            self._ctx.commit( )
        self.log.debug( 'Search vector purge complete.' )
        self.send( Packet.Reply( packet, { 'status':   200, 'text':     'Purge completed.'  } ) )

    def do_index(self, parameter, packet):

        try:
            object_id = long( parameter )
        except:
            self.send(Packet.Reply(packet, {'status':   500,
                                'text':     'Invald objectId specified.'  } ) )
            return

        self._create_entity_index( object_id )

    def do___audit_contact(self, parameter, packet):
        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index( object_id )

    def do___audit_document(self, parameter, packet):
        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index( object_id )

    def do___audit_enterprise(self, parameter, packet):
        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index( object_id )

    def do___audit_note(self, parameter, packet):
        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index( object_id )

    def do___audit_project(self, parameter, packet):
        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index( object_id )

    def do___audit_task(self, parameter, packet):
        object_id   = long( packet.data.get( 'objectId', 0 ) )
        action_tag  = packet.data.get( 'action', 'unknown' )
        if action_tag == '99_deleted':
            ## TODO: Delete any existing thumbnails
            pass
        self._create_entity_index( object_id )

    #
    # INDEXER Methods
    #

    def _create_entity_index(self, object_id):

        entity = self._ctx.type_manager.get_entity( object_id, repair_enabled=True )

        if entity:
            if not hasattr(self, '_index_{0}'.format(entity.__entityName__.lower())):
                self.log.debug( 'Entity type {0} not supported by index.'.format( entity.__entityName__ ) )
                return False
        else:
            self.log.debug( 'Cannot marshal objectId#{0}'.format( object_id ) )
            return False


        result = self._ctx.db_session().query(SearchVector).filter(SearchVector.object_id == object_id).all()

        if result:
            vector_entry = result[0]
            self.log.debug('Found search vector for objectId#{0}'.format(entity.object_id))
            if (vector_entry.version == entity.version) and (vector_entry.edition == INDEXER_EDITION):
                # We found an index entry and it is current, bail out
                self.log.debug('Search index for objectId#{0} is current'.format(entity.object_id))
                return False
            else:
                self.log.debug('Search vector for objectId#{0} is version {1}, entity is version {2}'.format(entity.object_id, vector_entry.version, entity.version))
        else:
            # We need to produce a new index entry
            self.log.debug( 'Creating new search vector for objectId#{0}/{1}'.format( object_id, entity.__entityName__ ) )
            vector_entry = SearchVector( entity.object_id, entity.__entityName__, entity.version, INDEXER_EDITION )
            self._ctx.db_session( ).add( vector_entry )

        index_function = getattr( self, '_index_{0}'.format(entity.__entityName__.lower( ) ) )

        try:
            vector_entry.keywords, \
                vector_entry.archived, \
                vector_entry.event_date, \
                text = index_function( entity )
        except UnicodeEncodeError, e:
            self._ctx.db_session( ).rollback( )
            self.send_administrative_notice( subject='Unicode error encountered indexing OGo#{0} [{1}]'.format( entity.object_id, entity.__entityName__ ),
                                             message=traceback.format_exc(),
                                             urgency=5,
                                             category='data' )
            return
        except AttributeError, e:
            self._ctx.db_session( ).rollback( )
            self.send_administrative_notice( subject='Attribute access error encountered indexing OGo#{0} [{1}]'.format( entity.object_id, entity.__entityName__ ),
                                             message=traceback.format_exc(),
                                             urgency=7,
                                             category='model' )
        except Exception, e:
            self._ctx.db_session( ).rollback( )
            self.send_administrative_notice( subject='A general exception occurred while indexing OGo#{0} [{1}]'.format( entity.object_id, entity.__entityName__ ),
                                             message=traceback.format_exc(),
                                             urgency=9,
                                             category='vista' )
        else:
            vector_entry.vector = func.to_tsvector( 'english', text )
            if hasattr( entity, 'project_id' ):
                vector_entry.project_id = entity.project_id
            else:
                vector_entry.project_id = None
            self._ctx.db_session( ).commit( )

    def _subindex_properties(self, entity, stream):
        for prop in self._ctx.property_manager.get_properties(entity):
            value = prop.get_value()
            if value:
                stream.write(normalize_string(str(value)))

    def _subindex_company(self, company, stream):
        for address in company.addresses.values( ):
            stream.write(normalize_string(address.city))
            stream.write(normalize_string(address.name1))
            stream.write(normalize_string(address.name2))
            stream.write(normalize_string(address.name3))
            stream.write(normalize_string(address.street))
            stream.write(normalize_string(address.province))
            stream.write(normalize_string(address.country))
            stream.write(normalize_string(address.district))
            stream.write(normalize_string(address.postal_code))

        for telephone in company.telephones.values( ):
            if telephone.number:
                tmp = telephone.number
                stream.write( normalize_string( tmp ) )
                stream.write( normalize_string( filter( type( tmp ).isdigit, tmp ) ) )
            if telephone.info:
                stream.write( normalize_string( telephone.info ) )

        for company_value in company.company_values.values( ):
            stream.write( normalize_string( company_value.name ) )
            if company_value.string_value:
                stream.write( normalize_string( company_value.string_value ) )

    def _index_task(self, task):
        stream = StringIO()

        keywords = archived = event_date = None

        stream.write(' {0} '.format(task.name))

        if task.state == '30_archived':
            archived = True
        else:
            archived = False

        keywords = parse_keywords(task.keywords, delimiter=' ')

        event_date = task.end

        stream.write(normalize_string(str(task.object_id)))
        stream.write(normalize_string(normalize_string(task.name)))
        stream.write(normalize_string(normalize_string(task.keywords)))
        stream.write(normalize_string(normalize_string(task.comment)))

        for note in task.notes:
            if note.comment:
                stream.write(normalize_string(note.comment))
            if note.action_date > event_date:
                event_date = note.action_date

        self._subindex_properties(task, stream)

        return keywords, archived, event_date, stream.getvalue()

    def _index_contact(self, contact):
        # TODO: parse associated_categories
        # TODO: associated_company
        # TODO: associated_contacts
        # TODO: include notes related to contact

        stream = StringIO( )

        keywords = archived = event_date = None

        if contact.status == 'archived':
            archived = True
        else:
            archived = False

        event_date = None

        keywords = parse_keywords( contact.keywords, delimiter=' ' )

        stream.write( normalize_string( str(contact.object_id ) ) )
        stream.write( normalize_string( contact.keywords ) )
        stream.write( normalize_string( contact.assistant_name ) )
        stream.write( normalize_string( contact.birth_name ) )
        stream.write( normalize_string( contact.birth_place ) )
        stream.write( normalize_string( contact.boss_name ) )
        stream.write( normalize_string( contact.citizenship ) )
        stream.write( normalize_string( contact.degree ) )
        stream.write( normalize_string( contact.department ) )
        stream.write( normalize_string( contact.display_name ) )
        stream.write( normalize_string( contact.family_status ) )
        stream.write( normalize_string( contact.last_name ) )
        stream.write( normalize_string( contact.middle_name ) )
        stream.write( normalize_string( contact.number ) )
        stream.write( normalize_string( contact.office ) )
        stream.write( normalize_string( contact.occupation ) )
        stream.write( normalize_string( contact.partner_name ) )
        stream.write( normalize_string( contact.file_as ) )
        stream.write( normalize_string( contact.comment ) )
        stream.write( normalize_datetime( contact.birth_date ) )
        stream.write( normalize_datetime( contact.grave_date ) )

        self._subindex_properties( contact, stream )

        self._subindex_company( contact, stream )

        for enterprise in self._ctx.run_command( 'contact::get-enterprises', object=contact ):
            stream.write( normalize_string( enterprise.name ) )
            stream.write( normalize_string( enterprise.bank_code ) )
            stream.write( normalize_string( enterprise.bank ) )
            for address in enterprise.addresses.values( ):
                stream.write( normalize_string( address.city ) )
                stream.write( normalize_string( address.province ) )
                stream.write( normalize_string( address.postal_code ) )
            for telephone in enterprise.telephones.values( ):
                if telephone.number:
                    stream.write( normalize_string( telephone.number ) )
                    stream.write( normalize_string( filter( type( telephone.number ).isdigit, telephone.number ) ) )

        return keywords, archived, event_date, stream.getvalue( )

    def _index_enterprise(self, enterprise):
        # TODO: parse associated_categories
        # TODO: associated_company
        # TODO: associated_contacts
        # TODO: include notes related to enterprse

        stream = StringIO()

        keywords = archived = event_date = None

        if enterprise.status == 'archived':
            archived = True
        else:
            archived = False

        event_date = None

        keywords = parse_keywords(enterprise.keywords, delimiter=' ')

        stream.write(normalize_string(str(enterprise.object_id)))
        stream.write(normalize_string(enterprise.keywords))
        stream.write(normalize_string(enterprise.bank_code))
        stream.write(normalize_string(enterprise.bank))
        stream.write(normalize_string(enterprise.file_as))
        stream.write(normalize_string(enterprise.number))
        stream.write(normalize_string(enterprise.number))
        stream.write(normalize_string(enterprise.comment))

        self._subindex_properties(enterprise, stream)

        self._subindex_company(enterprise, stream)

        return keywords, archived, event_date, stream.getvalue()
        t
    def _index_document(self, document):

        stream = StringIO()

        keywords = archived = event_date = None

        if document.status == 'archived':
            archived = True
        else:
            archived = False

        event_date = document.modified

        keywords = [ ]

        stream.write(normalize_string(document.name))
        stream.write(normalize_string(str(document.object_id)))
        stream.write(normalize_string(document.abstract))

        self._subindex_properties(document, stream)

        return keywords, archived, event_date, stream.getvalue()

    def _index_note(self, note):

        stream = StringIO()

        keywords = archived = event_date = None

        if note.status == 'archived':
            archived = True
        else:
            archived = False

        event_date = note.modified

        keywords = [ ]

        stream.write(normalize_string(note.title))
        stream.write(normalize_string(str(note.object_id)))
        stream.write(normalize_string(note.abstract))

        try:
            if note.content:
                text = note.content.encode('ascii', 'xmlcharrefreplace')
                stream.write(text)
        except UnicodeDecodeError, e:
            self.send_administrative_notice(
                subject='Content encoding error indexing noteId#{0}'.format(note.object_id),
                message='{0}\n{1}'.format(e, traceback.format_exc()),
                urgency=4,
                category='document')

        self._subindex_properties(note, stream)

        return keywords, archived, event_date, stream.getvalue()


    def _index_project(self, project):
        # TODO: Index name of assigned contacts & enterprises
        stream = StringIO()

        keywords = archived = event_date = None

        stream.write(' {0} {1}'.format(project.name, project.number))

        if project.status == 'archived':
            archived = True
        else:
            archived = False

        keywords = None

        event_date = None

        stream.write(normalize_string(str(project.object_id)))
        stream.write(normalize_string(normalize_string(project.kind)))
        stream.write(normalize_string(normalize_string(project.comment)))

        self._subindex_properties(project, stream)

        return keywords, archived, event_date, stream.getvalue()
