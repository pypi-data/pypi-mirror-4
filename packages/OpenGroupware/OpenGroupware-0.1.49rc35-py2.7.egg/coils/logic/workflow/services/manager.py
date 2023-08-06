#
# Copyright (c) 2010, 2012, 2013
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
from time             import time  # NOTE: only used from scheduling
from sqlalchemy       import and_, or_
from sqlalchemy.orm   import aliased
from coils.core       import Process, Route, ObjectProperty, AdministrativeContext, Service, Packet

class ManagerService(Service):
    __service__ = 'coils.workflow.manager'
    __TimeOut__ = 60

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._enabled  = True
        self._ctx = AdministrativeContext({}, broker=self._broker)
        self._last_time = time()
        self._ps = { }
        self.send( Packet( 'coils.workflow.manager/ticktock', 'coils.clock/subscribe', None ) )

    @property
    def ps(self):
        return self._ps

    def manager_register_process(self, _process, status = '?', executor_id = '', run_token=None):
        '''
        Make the manager aware of the specified process and record it in the requested state.

        :param _process: Either a Process entity or a process id
        :param status: The status to record for the process
        :param executor_id: The executor of the process, currently blank.  This is a place holder
        for the implementation of multiple executors.
        :param run_token: The run token / run lock of the process.
        '''

        if isinstance(_process, Process):
            pid = long( _process.object_id )
            process = _process
        elif isinstance( _process, int ) or isinstance( _process, long ):
            pid = long( _process )
            process = None
        else:
            raise CoilsException( 'Can only register a process by entity or pid, got a "{0}"'.format( type( _process) ) )
        _process = None

        if pid not in self.ps:
            # this process is not already registered, so learn about it

            if not process:
                process = self._ctx.run_command( 'process::get', id=pid )
                if not process:
                    self.log.info( 'Cannot marshall OGo#{0}, discarding registration request.'.format( pid ) )
                    return False

            if process.state in ( 'X', 'F', ):
                self.log.info( 'OGo#{0} [Process] in state "{1}", refusing registration'.format( process.object_id, process.state ) )
                return False

            singleton = False
            routegroup= str( process.object_id )
            if process.route:
                if process.route.route_group:
                    routegoup =  process.route.route_group.name.upper( )
                else:
                    routegoup =  process.route.name.upper( )
                if process.route.is_singleton:
                    singleton = True
            else:
                self.log.error( 'No route found for OGo#{0} [Process]; refusing registration.'.format( process.object_id, ) )
                # TODO: Send adminsitrative notice
                return False

            # NOTE: the executorId value is to identify the executor that own the process,
            #       or owned the process last.  This is for *future* support of multiple
            #       executors.
            self.ps[ pid ] = { 'processId':  process.object_id,
                               'contextId':  process.owner_id,
                               'status':     '?',
                               'executor':   executor_id,
                               'routeGroup': routegroup,
                               'registered': time(),
                               'routeId': 0,
                               'routeName': 'n/a',
                               'lockToken':  None,
                               'singleton':  singleton }

            if process.route:
                self.ps[process.object_id]['routeId'] = process.route.object_id
                self.ps[process.object_id]['routeName'] =  process.route.name

            # Set the contextName, used in process listings such as available in snurtle
            if process.owner_id == 8999:
                self.ps[ pid ][ 'contextName' ] = 'Coils\Network'
            elif process.owner_id == 0:
                self.ps[ pid ][ 'contextName' ] = 'Coils\Anonymous'
            elif process.owner_id == 10000:
                self.ps[ pid ][ 'contextName' ] = 'Coils\Administrator'
            elif process.owner_id > 10000:
                owner = self._ctx.run_command( 'contact::get', id=process.owner_id )
                if owner:
                    self.ps[ pid ][ 'contextName' ] = owner.login
                    owner = None
                else:
                    self.ps[ pidd ][ 'contextName' ] = 'OGo{0}'.format( process.owner_id )
            else:
                self.ps[ pid ][ 'contextName' ] = '_undefined_'

            self.log.debug( 'New OGo#{0} [Process] registered; routeGroup="{1}" singleton="{2}"'.format( pid, routegroup, singleton ) )

        self.ps[ pid ][ 'status' ]  = status
        self.ps[ pid ][ 'updated' ] = time( )

        if run_token:
            self.ps[ pid ][ 'lockToken' ] = run_token.strip( )
        self.log.debug( 'OGo#{0} [Process] registered in state "{1}"'.format( pid, status ) )

        if status == 'R' and pid: self.manager_refresh_run_lock( pid )

        return True

    def manager_get_run_locktoken(self, pid):

        lock_token = None
        if pid in self.ps:
            lock_token = self.ps[ pid ][ 'lockToken' ]
            self.log.debug( 'Deregistered OGo#{0} [Process]'.format( pid ) )

        # Verify run-lock token between registration and database
        prop = self._ctx.property_manager.get_property( pid, 'http://www.opengroupware.us/oie', 'lockToken' )
        if prop and lock_token:
            if lock_token != prop.get_value( ).strip( ):
                self.log.error( 'Run lock token mismatch detected for OGo#{0}!  Registered lock token is "{1}" but found lock token of "{2}"'.\
                    format( pid, lock_token, prop.get_value ) )
                self.log.warn( 'Workflow manager has no choice but to wait for run lock expiration.' )
                return False
            self.log.debug( 'Registered run lock token matches lock token discovered.' )
            prop = None
        elif not lock_token:
            lock_token = prop.get_value( ).strip( )
            self.log.info( 'No run lock token was registered, discovered token "{0}" for OGo#{1}'.format( lock_token, pid ) )
        elif not prop:
            self.log.info( 'No run lock token discovered for OGo#{1}, but a token was registered.'.format( pid ) )

        return lock_token

    def manager_refresh_run_lock(self, pid):

        lock_token = self.manager_get_run_locktoken( pid )
        if lock_token:
            if not self._ctx.lock_manager.administratively_refresh_lock( lock_token, duration=360000 ):
                self.log.warn( 'Run lock for OGo#{0} not refreshed!'.format( pid ) )
            else:
                self.log.debug( 'Run lock for OGo#{0} [Process] refreshed.'.format( pid ) )
        else:
            self.log.error( 'Could not find lock token for OGo#{0} [Process]; not refreshed!'.format( pid ) )

    def manager_deregister_process(self, process):

        if isinstance(process, Process):
            pid = long( process.object_id )
        elif isinstance( process, int ) or isinstance( process, long ):
            pid = long( process )
        else:
            raise CoilsException( 'Can only deregister a process by entity or objectId, got a "{0}"'.format( type( process ) ) )

        lock_token = self.manager_get_run_locktoken( pid )

        # Release the run lock
        if lock_token:
            if not self._ctx.lock_manager.administratively_release_lock( lock_token ):
                self.log.warn( 'Run lock for OGo#{0} not found to be removed!'.format( pid ) )
            else:
                self.log.debug( 'Removed run lock for OGo#{0} [Process]'.format( pid ) )
        else:
            self.log.error( 'Requested to deregister a process for which there was no lock token' )

        if pid in self.ps:
            del self.ps[ pid ]
            self.log.info( 'Registration of OGo#{0} deleted'.format( pid ) )

        return False

    #
    # Internal methods
    #

    def manager_request_process_start(self, pid, cid):
        self.log.debug( 'Requesting process start for OGo#{0}'.format( pid ) )
        self.manager_register_process( pid, status='/' )
        self.send( Packet( 'coils.workflow.manager/is_running',
                           'coils.workflow.executor/start',
                           { 'processId': pid,
                             'contextId': cid } ) )


    def manager_scan_running_processes(self):
        self.log.info( 'Checking processes we believe in running state' )
        db = self._ctx.db_session()
        # Discover all the PIDs that are recorded in the database as running
        running_pids = [ x[0] for x in db.query(Process.object_id).filter(Process.state=='R').all() ]
        # Discover if the manager has any PIDs it believes are running but are
        # not in a running state in the database
        for pid in self.ps:
            if self.ps[ pid ][ 'status' ] == 'R':
                if pid not in running_pids:
                    running_pids.append( pid )
        # If we found any running processes request from their executor if they are running
        if running_pids:
            self.log.info( 'Found {0} processes in running state'.format( len( running_pids ) ) )
            for pid in running_pids:
                self.send(Packet('coils.workflow.manager/is_running',
                                 'coils.workflow.executor/is_running:{0}'.format(pid),
                                 None))
                if pid not in self.ps:
                    process = db.query(Process).filter(Process.object_id == pid).all()
                    if process:
                        self.manager_register_process(process[0], status='?')
        else:
            self.log.info('Found no processes in running state')
        self._ctx.commit()
        self.log.debug( 'Scan running processes commit.')

    def manager_start_queued_processes(self):

        if not self._enabled:
            self.log.info(' Workflow manager is in a disbaled state, will not start new processes.' )
            return
        self.log.info('Checking for queued processes')

        db = self._ctx.db_session()
        try:

            query = db.query( Process, Route ).\
                    join( Route, Route.object_id == Process.route_id ).\
                    filter( and_( Process.state.in_( [ 'Q' ] ),
                                  Process.status != 'archived' ) ).\
                    order_by(Process.priority.desc(), Process.object_id).\
                    limit(150)
            result = query.all( )

            for process, route in result:

                context_id  = self._ctx.account_id
                if route.is_singleton:
                    context_id = process.object_id

                lock_target = route.route_group
                if not lock_target:
                    lock_target = route

                locked, my_lock = self._ctx.lock_manager.lock( entity = lock_target,
                                                               duration = 3600,
                                                               data = str( process.object_id ),
                                                               run = True,
                                                               context_id = context_id )
                if locked:
                    self._ctx.property_manager.set_property( process, 'http://www.opengroupware.us/oie', 'lockToken', my_lock.token )
                    self.log.info('Workflow manager acquired lock "{0}" on OGo#{1} as OGo#{2} in order to start OGo#{3}'.\
                        format( my_lock.token.strip( ), lock_target.object_id, context_id, process.object_id ) )
                    self.manager_register_process( process, status='Q', run_token=my_lock.token )
                    self.manager_request_process_start( process.object_id, process.owner_id )
                else:
                    self.log.info('Manager unable to acquire lock on OGo#{0} as OGo#{0} in order to start OGo#{2}'.\
                        format( lock_target.object_id, context_id, process.object_id ) )
                self._ctx.flush( )

        except Exception, e:
            self.log.exception(e)

        self._ctx.commit()
        self.log.debug( 'Start Queueud Processes Commit')

    def manager_detect_zombie(self, process_id):
        process = self._ctx.run_command( 'process::get', id = process_id )

        if not process:
            self.log.debug( 'Can find no such process as OGo#{0}'.format( process_id ) )
            return

        if process.state == 'C':
            self.send( Packet( None, 'coils.workflow.manager/completed:{0}'.format( process_id ), None ) )
            self.log.debug( 'Suspected Zombie process was in state complete, ignored.' )
            return
        elif process.state == 'F':
            self.send( Packet( None, 'coils.workflow.manager/failed:{0}'.format( process_id ), None ) )
            self.log.debug( 'Suspected Zombie process was in state failed, ignored.' )
            return
        elif not process.state == 'R':
            self.log.debug( 'Not a Zombie, OGo#{0} [Process] in state "{1}", not in state "running"'.format( process_id, process.state ) )
            return

        self.log.warn( 'Processing OGo#{0} [Process] as a zombie.'.format( process_id ) )

        ''' Generate a very descriptive message for the process we have determined has
            become one of the living dead. '''

        route_id = process.route_id
        if process.route:
            route_name = process.route.name
        else:
            route_name = 'n/a'

        owner = self._ctx.run_command( 'contact::get', id=process.owner_id )
        if owner:
            owners_name = owner.login
        else:
            owners_name = 'n/a'

        process_messages = self._ctx.run_command('process::get-messages', process=process)
        process_messages = [ '    UUID#{0} \n' \
                             '      Version:{1} Size:{2} Label:{3}'.format(x.uuid, x.version, x.size, x.label)
                             for x in process_messages ]

        message = 'objectId#{0} [Process] determined to be in zombie state.\n' \
                  '  Route: {1} "{2}"\n' \
                  '  Owner: {3} "{4}"\n' \
                  '  Version: {5}\n' \
                  '  Messages:\n' \
                  '{6}'.format( process.object_id,
                                route_id, route_name,
                                process.owner_id, owners_name,
                                process.version,
                                '\n'.join(process_messages))

        self.send_administrative_notice(
            category='workflow',
            urgency=3,
            subject='OGo#{0} [Process] Flagged As Zombie'.format(process_id),
            message=message)

        process.state = 'Z'
        self.manager_deregister_process(process_id)
        self._ctx.commit()
        self.log.debug( 'Zombie check commit.' )


    #
    # message receivers
    #

    def do_ticktock(self, parameter, packet):
        if self._enabled:
            if ((time() - self._last_time) > 180):
                self.log.debug('Running maintenance processes')
                self.manager_scan_running_processes()
                self.manager_start_queued_processes()
                self._last_time = time()

    def do_checkqueue(self, parameter, packet):
        self.manager_start_queued_processes()
        self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
        return

    def do_disabled(self, parameter, packet):
        self._enabled = False
        self.log.info( 'DoDisable: Workflow manager is now disabled, now new processes will be started.' )
        return

    def do_enable(self, parameter, packet):
        self._enabled = True
        self.log.info( 'DoDisable: Workflow manager is now enabled, new processes may be started.' )
        return

    def do_failed(self, parameter, packet):
        process_id = long( parameter )
        self.log.info( 'DoFail: Request to mark OGo#{0} [Process] as failed.'.format( process_id ) )
        process = self._ctx.run_command( 'process::get', id=process_id )
        if process:
            if process.state == 'R':
                # A process may mark *ITSELF* as failed, but since something went wrong
                # this is here as a double-check.
                self.log.warn( 'DoFail: Marking "running" OGo#{0} [Process] as failed.'.format( process_id ) )
                self.send_administrative_notice(
                        category='workflow',
                        urgency=4,
                        subject='Defunct OIE Worker Detected',
                        message='Detected OGo#{0} [Process] in defunct state, process will be failed.'.format( process_id ) )
                process.state = 'F'
                self._ctx.commit( )
                self.send( Packet( None,
                                  'coils.workflow.logger/log',
                                  { 'process_id': process_id,
                                    'message': 'Manager set state of process to failed.' } ) )
            self.manager_deregister_process( process_id )
        else:
            self.log.debug( 'DoFail: OGo#{0} [Process] not found'.format( process_id ) )

    def do_completed(self, parameter, packet):
        process_id = long( parameter )
        self.log.info( 'DoComplete: OGo#{0} [Process] reported completed'.format( process_id ) )
        self.manager_deregister_process( process_id )
        self.manager_start_queued_processes( )

    def do_parked(self, parameter, packet):
        process_id = long( parameter )
        self.log.info( 'DoParked: OGo#{0} [Process] reported parked'.format( process_id ) )
        self.manager_deregister_process( process_id )
        self.manager_start_queued_processes( )

    def do_is_running(self, parameter, packet):
        pid = long( packet.data[ 'processId' ] )
        if packet.data[ 'running' ] == 'YES':
            self.log.info( 'DoIsRunning: OGo#{0} [Process] reported as running'.format( pid ) )
            self.manager_register_process( pid, status='R' )
        else:
            self.log.info( 'DoIsRunning: OGo#{0} [Process] reported as not running'.format( pid ) )
            self.manager_detect_zombie( pid )

    def do_queue(self, parameter, packet):
        process_id = long( parameter )
        self.log.debug( 'DoQueue: Request to queue OGo#{0} [Process].'.format( process_id ) )
        self.send( Packet( None, 'coils.workflow.logger/log',
                           { 'process_id': process_id,
                             'message': 'Request to place in queued state.'  } ) )
        process = self._ctx.run_command( 'process::get', id=process_id )
        if process:
            if process.state in ( 'I', 'H', 'P' ):
                process.state = 'Q'
                self._ctx.commit( )
                self.log.debug( 'DoQueue: OGo#{0} [Process] committed into queued state'.format( process_id ) )
                self.send( Packet.Reply( packet, { 'status': 201, 'text': 'OK' } ) )
                self.manager_start_queued_processes( )
            elif process.state == 'Q':
                self.log.debug( 'DoQueue: OGo#{0} [Process] already in queued state'.format( process_id ) )
                self.send( Packet( None,
                                   'coils.workflow.logger/log',
                                   { 'process_id': process_id,
                                     'message': 'Process is already in queued state' } ) )
                self.send( Packet.Reply( packet, { 'status': 201,
                                                  'text': 'OK, No action.' } ) )
            else:
                self._ctx.rollback( )
                self.log.info( 'DoQueue: OGo#{0} [Process] cannot be queued from state "{1}"'.format( process_id, process.state ) )
                message = 'OGo#{0} [Process] cannot be queued from state "{1}"'.format( process_id, process.state )
                self.send( Packet( None, 'coils.workflow.logger/log',
                                   { 'process_id': process_id,
                                     'message': message } ) )
                self.send( Packet.Reply( packet, { 'status': 403, 'text': message } ) )
        else:
            self.log.warn( 'DoQueue: Request to queue OGo#{0} [Process] but process could not be found.'.format( process_id ) )
            self.send( Packet.Reply(packet, { 'status': 404, 'text': 'No such process' } ) )

    def do_ps(self, parameter, packet):
        self.send( Packet.Reply( packet, { 'status': 200,
                                           'text': 'OK',
                                           'processList': self.ps.values( ) } ) )
