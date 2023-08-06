#
# Copyright (c) 2013
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
import select
import psycopg2
import psycopg2.extensions
from sqlalchemy       import and_, func
from threading        import Thread
from threading        import local as thread_local
from coils.core       import *


EVENTQUEUE='auditEvent';

WATCHER_NAMESPACE = '817cf521c06b47228392a0437daf81e0'
WATCHER_TIMEOUT   = 1000
WATCHER_NOTIFY    = 1001
WATCHED_TYPES     = [ 'document', 'contact',     'enterprise', 'task',
                      'project',  'appointment', 'folder',     'note',
                      'route',    'process', ]
NOTIFY_EXCHANGE = 'OpenGroupware_Coils_Notify'


def watch_for_pgevents(service):

    event_queue = service.event_queue

    t = thread_local()
    t.ctx = AdministrativeContext( )
    conn = t.ctx.db_session( ).connection( ).connection.checkout( ).connection
    conn.set_isolation_level( psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT )
    curs = conn.cursor( )
    curs.execute( 'LISTEN {0};'.format( EVENTQUEUE ) )

    while service.RUNNING:
        if select.select( [ conn ], [ ], [ ], 15 ) == ( [ ], [ ], [ ] ):
            event_queue.put( (WATCHER_TIMEOUT, None, ) )
        else:
            conn.poll( )
            while conn.notifies:
                notify = conn.notifies.pop( )
                payload = notify.payload
                event_queue.put( ( WATCHER_NOTIFY, None, ) )
    t.ctx.close( )


class WatcherService (ThreadedService):
    __service__ = 'coils.watcher'
    __auto_dispatch__ = True

    def __init__(self):
        ThreadedService.__init__(self)
        self.threads[ 'audit']     = Thread( target=watch_for_pgevents,
                                             name='pgListen',
                                             args=( self, ) )
        self.max_audit_entry = 0

    def prepare(self):
        ThreadedService.prepare(self)
        self._ctx = AdministrativeContext( { }, broker=self._broker )
        self._sd = ServerDefaultsManager()

        prop = self._ctx.property_manager.get_server_property( WATCHER_NAMESPACE, 'maxAuditEntry' )
        if prop:
            self.max_audit_entry = long( prop.get_value( ) )
        else:
            self.max_audit_entry = self._ctx.db_session( ).query( func.max( AuditEntry.object_id ) ).one( )[0]
            self.persist_max_audit_entry( )
            self._ctx.commit( )

    def process_service_specific_event(self, event_class, event_data):
        if event_class == WATCHER_TIMEOUT:
            pass
        elif event_class == WATCHER_NOTIFY:
            self.perform_collect_changes( )
            self.persist_max_audit_entry( )
    #
    # Perform Handlers
    #

    def perform_collect_changes(self):
        '''
        Collect changs from the audit log.

        00_created,
        02_rejected,
        27_reactivated,
        download
        25_done,
        10_archived
        99_delete
        10_commented
        05_changed
        30_archived
        '''
        query = self._ctx.db_session().query( AuditEntry ).\
                    filter( and_ ( AuditEntry.object_id > self.max_audit_entry ,
                                   AuditEntry.action.in_( [ '00_created', '05_changed',
                                                            '99_deleted', ] ) ) ).\
                    order_by( AuditEntry.object_id )
        for event in query.all( ):
            kind = self._ctx.type_manager.get_type( event.context_id ).lower( )
            if kind in WATCHED_TYPES:
                self.log.debug( 'Sending event notification for OGo#{0} [{1}] "{2}"'.format( event.context_id, kind, event.action ) )
                self.send( Packet( None,
                                   'coils.notify/__audit_{0}'.format( kind ),
                                   { 'auditId':  event.object_id,
                                     'kind':     kind,
                                     'objectId': event.context_id,
                                     'actorId':  event.actor_id,
                                     'action':   event.action,
                                     'message':  event.message } ), fanout=True, exchange=NOTIFY_EXCHANGE )
            self.max_audit_entry = event.object_id
        self.persist_max_audit_entry( )
        self._ctx.commit( )

    def persist_max_audit_entry(self):
        self._ctx.property_manager.set_server_property( WATCHER_NAMESPACE, 'maxAuditEntry', self.max_audit_entry )

    #
    # Message Handlers
    #

    def do_set_maxauditentry(self, parameter, packet):
        object_id   = long( packet.data.get( 'maxAuditEntry', 0 ) )
        if object_id:
            self.log.info( 'Request to reset "maxAuditEntryValue" to {0}'.format( object_id ) )
            self.max_audit_entry = object_id
            self.persist_max_audit_entry( )

    def do_get_maxaudit_entry(self, parameter, packet):
        self.send( Packet.Reply( packet, { 'status': 200,
                                           'text': 'coils.watcher maxAuditEntry',
                                           'value': self.max_audit_entry } ) )
