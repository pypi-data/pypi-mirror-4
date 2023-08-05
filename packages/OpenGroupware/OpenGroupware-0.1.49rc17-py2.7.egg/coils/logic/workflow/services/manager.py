#
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
        
    def manager_register_process(self, _process, status = '?', executor_id = ''):
        
        if isinstance(_process, Process):
            pid = _process.object_id
            process = _process
        elif isinstance(_process, int):
            pid = _process
            process = None
        else:
            raise CoilsException('Can only register a process by entity or pid, got a "{0}"'.format(type(_process)))
        _process = None
        
        if pid not in self.ps:
        
            if not process:
                process = self._ctx.run_command('process::get', id=pid)
                if not process:
                    return False
            
            routegroup = None
            if process.route:
                prop = self._ctx.property_manager.get_property(process.route, 'http://www.opengroupware.us/oie', 'routeGroup')
                if prop:
                    routegroup = prop.get_value()
                else:
                    routegroup = str(process.route.name)
            else:
                routegroup = str(process.object_id)
            routegroup = routegroup.upper()
                
            singleton = False
            if process.route:
                prop = self._ctx.property_manager.get_property(process.route, 'http://www.opengroupware.us/oie', 'singleton')
                if prop:
                    value = prop.get_value()
                    if isinstance(value, basestring):
                        if value.upper() == 'YES':
                            singleton = True
                            
            # NOTE: the executorId value is to identify the executor that own the process,
            #       or owned the process last.  This is for *future* support of multiple
            #       executors.
            self.ps[process.object_id] = { 'processId':  process.object_id,
                                           'contextId':  process.owner_id,
                                           'status':     '?',
                                           'executor':   executor_id,
                                           'routeGroup': routegroup,
                                           'registered': time(),
                                           'routeId': 0,
                                           'routeName': 'n/a',
                                           'singleton':  singleton }
                                           
            if process.route:
                self.ps[process.object_id]['routeId'] = process.route.object_id
                self.ps[process.object_id]['routeName'] =  process.route.name
                
            # Set the contextName, used in process listings such as available in snurtle
            if process.owner_id == 8999:
                self.ps[ process.object_id ][ 'contextName' ] = 'Coils\Network'
            elif process.owner_id == 0:
                self.ps[ process.object_id ][ 'contextName' ] = 'Coils\Anonymous'
            elif process.owner_id == 10000:
                self.ps[ process.object_id ][ 'contextName' ] = 'Coils\Administrator'                
            elif process.owner_id > 10000:
                owner = self._ctx.run_command( 'contact::get', id=process.owner_id )
                if owner:
                    self.ps[ process.object_id ][ 'contextName' ] = owner.login
                    owner = None
                else:
                    self.ps[ process.object_id ][ 'contextName' ] = 'OGo{0}'.format( process.owner_id )
            else:
                self.ps[ process.object_id ][ 'contextName' ] = '_undefined_'
                
            self.log.debug('New OGo#{0} [Process] registered; routeGroup="{1}" singleton="{2}"'.format(pid, routegroup, singleton))
                                           
        self.ps[pid]['status']  = status
        self.ps[pid]['updated'] = time()
        self.log.debug('OGo#{0} [Process] registered in state "{1}"'.format(pid, status))
        return True
                                       
    def manager_deregister_process(self, process):
        if isinstance(process, Process):
            pid = process.object_id
        elif isinstance(process, int):
            pid = process
        else:
            raise CoilsException('Can only deregister a process by entity or objectId, got a "{0}"'.format(type(process)))
        self.log.debug( 'Discarding OGo#{0} [Process] registration."'.format( pid ) )
        if pid in self.ps:
            del self.ps[pid]
            return True
        return False

    #
    # Internal methods
    #

    def manager_request_process_start(self, pid, cid):
        self.log.debug('Requesting process start for OGo#{0}'.format(pid))
        self.manager_register_process(pid, status='/')
        self.send( Packet( 'coils.workflow.manager/is_running',
                           'coils.workflow.executor/start',
                           { 'processId': pid,
                             'contextId': cid } ) )
                           

    def manager_scan_running_processes(self):
        self.log.info('Checking processes we believe in running state')
        db = self._ctx.db_session()
        # Discover all the PIDs that are recorded in the database as running
        running_pids = [ x[0] for x in db.query(Process.object_id).filter(Process.state=='R').all() ]
        # Discover if the manager has any PIDs it believes are running but are
        # not in a running state in the database
        for pid in self.ps:
            if self.ps[pid]['status'] == 'R':
                if pid not in running_pids:
                    running_pids.append(pid)
        # If we found any running processes request from their executor if they are running
        if running_pids:
            self.log.info('Found {0} processing in running state'.format(len(running_pids)))
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

    def manager_start_queued_processes(self):
        self.log.info('Checking for queued processes')
        db = self._ctx.db_session()
        try:
            
            op1 = aliased(ObjectProperty)
            op2 = aliased(ObjectProperty)
            query = db.query( Process, op1, op2 ).\
                    join( Route, Route.object_id == Process.route_id ).\
                    outerjoin( op1, and_( op1.parent_id == Route.object_id, 
                        op1.namespace=='http://www.opengroupware.us/oie',
                        op1.name=='singleton' ), ).\
                    outerjoin( op2, and_( op2.parent_id == Route.object_id, 
                        op2.namespace=='http://www.opengroupware.us/oie',
                        op2.name=='routeGroup' ), ).\
                    filter( and_( Process.state.in_( [ 'Q' ] ), 
                                  Process.status != 'archived' ) ).\
                    order_by(Process.priority.desc(), Process.object_id).\
                    limit(150)
                    
            for process, sp, rp in query.all():
                
                is_singleton = False
                if sp:
                    value = sp.get_value()
                    if isinstance(value, basestring):
                        if value.upper() == 'YES':
                            is_singleton = True
                
                route_group = str(process.object_id)   
                if rp:
                    value = rp.get_value()
                    if value:
                        route_group = value
                route_group = route_group.upper()
                        
                if is_singleton:
                    if [ x for x in self.ps.values() if x['routeGroup'] == route_group ]:
                        # A singleton in this routeGroup already exists, avoid registration and start
                        self.log.info('Singleton in routeGroup "{0}" already registered, not considering OGo#{1} [Process]'.format(route_group, process.object_id))
                        process = [ x for x in self.ps.values() if x['routeGroup'] == route_group ]
                        if process:
                            process = process[0]
                            self.log.info('routeGroup "{0}" singleton blocked by OGo#{1} [Process]'.format(process['routeGroup'], process['processId']))
                        continue

                self.manager_register_process(process, status='Q')
                self.manager_request_process_start(process.object_id, process.owner_id)
            
        except Exception, e:
            self.log.exception(e)
            
        self.log.info('Checking for queued complete')
        self._ctx.commit()
        self.log.info('Committed.')

    def manager_detect_zombie(self, process_id):
        process = self._ctx.run_command('process::get', id = process_id)
        if process:
            if process.state == 'R':
                
                self.log.warn('Marking running OGo#{0} [Process] as zombie.'.format(process_id))
                
                ''' Generate a very descriptive message for the process we have determined has 
                    become one of the living dead. '''
                
                route_id = process.route_id
                if process.route:
                    route_name = process.route.name
                else:
                    route_name = 'n/a'
                
                owner = self._ctx.run_command('contact::get', id=process.owner_id)
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
                
            elif process.state == 'C':
                self.send( Packet( None, 'coils.workflow.manager/completed:{0}'.format(process_id), None ) )
            elif process.state == 'F':
                self.send( Packet( None, 'coils.workflow.manager/failed:{0}'.format(process_id), None ) )
            else:
                self.log.warn('State of potential zombie OGo#{0} [Process] is "{1}"'.format(process_id, process.state))

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
        return

    def do_enable(self, parameter, packet):
        self._enabled = True
        return

    def do_failed(self, parameter, packet):
        process_id = int(parameter)
        self.log.info('Request to mark OGo#{0} [Process] as failed.'.format(process_id))
        process = self._ctx.run_command('process::get', id=process_id)
        if process:
            if process.state == 'R':
                # A process may mark *ITSELF* as failed, but since something went wrong
                # this is here as a double-check.
                self.log.warn('Marking "running" OGo#{0} [Process] as failed.'.format(process_id))
                self.send_administrative_notice(
                        category='workflow',
                        urgency=4,
                        subject='Defunct OIE Worker Detected',
                        message='Detected OGo#{0} [Process] in defunct state, process will be failed.'.format(process_id))
                process.state = 'F'
                self._ctx.commit()
                self.send(Packet(None,
                                 'coils.workflow.logger/log',
                                 { 'process_id': process_id,
                                   'message': 'Manager set state of process to failed.' } ) )
        self.manager_deregister_process(process_id)
        
    def do_completed(self, parameter, packet):
        process_id = int(parameter)
        self.log.info('OGo#{0} [Process] reported completed'.format(process_id))
        self.manager_deregister_process(process_id)
        self.manager_start_queued_processes()

    def do_is_running(self, parameter, packet):
        process_id = packet.data['processId']
        if packet.data['running'] == 'YES':
            self.log.info('OGo#{0} [Process] reported as running'.format(process_id))
            self.manager_register_process(process_id, status='R')
        else:
            self.log.info('OGo#{0} [Process] reported as not running'.format(process_id))
            self.manager_detect_zombie(process_id)

    def do_queue(self, parameter, packet):
        process_id = int(parameter)
        self.send( Packet( None, 'coils.workflow.logger/log',
                           { 'process_id': process_id,
                             'message': 'Request to place in queued state.'  } ) )
        process = self._ctx.run_command('process::get', id=process_id)
        if process:
            if process.state in ( 'I', 'H', 'P' ):
                process.state = 'Q'
                self._ctx.commit()
                self.send( Packet.Reply( packet, { 'status': 201, 'text': 'OK' } ) )
                self.manager_start_queued_processes()
            elif (process.state == 'Q'):
                self.send( Packet( None,
                                   'coils.workflow.logger/log',
                                   { 'process_id': process_id,
                                     'message': 'Process is already in queued state' } ) )
                self.send( Packet.Reply( packet, { 'status': 201,
                                                  'text': 'OK, No action.' } ) )
            else:
                self._ctx.rollback()
                message = 'OGo#{0} [Process] cannot be queued from state "{1}"'.format(process_id, process.state)
                self.send( Packet( None, 'coils.workflow.logger/log',
                                   { 'process_id': process_id,
                                     'message': message } ) )
                self.send( Packet.Reply( packet, { 'status': 403, 'text': message } ) )
        else:
            self.log.warn('Request to queue OGo#{0} [Process] but process could not be found.'.format(process_id))
            self.send( Packet.Reply(packet, { 'status': 404, 'text': 'No such process' } ) )
            
    def do_ps(self, parameter, packet):
        self.send( Packet.Reply( packet, { 'status': 200,
                                           'text': 'OK',
                                           'processList': self.ps.values( ) } ) )                                       
