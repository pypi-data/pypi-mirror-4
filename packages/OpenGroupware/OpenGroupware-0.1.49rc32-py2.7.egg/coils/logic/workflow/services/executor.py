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
from time             import time
from coils.core       import *
from process          import Process as WFProcess
import multiprocessing

EXECUTOR_MAX_WORKERS = 10

def start_workflow_process(p, c):
    w = WFProcess(p, c)
    w.run()


class ExecutorService(Service):
    __service__ = 'coils.workflow.executor'
    __auto_dispatch__ = True
    __is_worker__     = False

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._workers = { }
        self.send(Packet('coils.workflow.executor/ticktock',
                         'coils.clock/subscribe',
                         None))
        self._pending = { }

    def executor_start_process(self, process_id, context_id):
        if (process_id is None):
            self.log.error('Received request to start a NULL processId!')
            return False
        if len(self._workers) < EXECUTOR_MAX_WORKERS:
            return self.executor_create_worker(process_id, context_id = context_id)
        else:
            self.log.debug('Too many workers already running; not starting OGo#{0} [Process]'.format(process_id))
            return False
        
    def executor_restart_process(self, process_id, context_id):
        ''' A method to restart a process if the process is not already running.  Really there
            is no difference between a start and a restart. '''
        self.executor_start_process(process_id, context_id)
        
    def executor_verify_worker(self, pid):
        if pid in self._workers:
            
            if not self._workers[pid]['process']:
                return False
                
            self._workers[pid]['process'].join(0.1)
            if self._workers[pid]['process'].is_alive():
                # Worker is ALIVE!
                
                self.send( Packet( None, 'coils.workflow.logger/log',
                                   { 'process_id': pid,
                                     'category':   'control',
                                      'message':    'Verified life of worker' } ) )
                                      
                self.send( Packet( None, 'coils.workflow.manager/is_running',
                                   { 'status':    200,
                                     'text':      'Running',
                                     'running':   'YES',
                                     'processId': pid } ) )
                                     
                return True
                
            else:
                
                # Worker is *NOT* alive
                
                self.log.info('Worker for OGo#{0} [Process] in state "{1}" is gone.'.format( pid, self._workers[pid]['status'] ) )
                
                
                if self._workers[pid]['status'] == 'running':
                    # We think the process should be running
                    self.log.info('Worker for OGo#{0} [Process] is defunct in state "{1}"'.format(pid, self._workers[pid]['status']))
                    self.send(Packet( None, 'coils.workflow.logger/log',
                                      { 'process_id': pid,
                                        'category': 'control',
                                        'message': 'Detected defunct worker with state "{0}"'.format(self._workers[pid]['status']) } ) )
                    return False
                                        
                
                self.send(Packet( None, 'coils.workflow.logger/log',
                                  { 'process_id': pid,
                                    'category': 'control',
                                    'message': 'Expired worker in state "{0}"'.format(self._workers[pid]['status']) } ) )
                
                # Tell the manager this worker is not longer alive
                self.send( Packet( None, 'coils.workflow.manager/is_running',
                                   { 'status':    200,
                                     'text':      'Not running',
                                     'running':   'NO',
                                     'processId': pid } ) ) 
                                                                    
            if self._workers[pid]['status'] != 'started':
                return False
        
    def executor_delist_worker(self, process_id):
        if self.executor_verify_worker(process_id):
            return False
        else:
            if process_id in self._workers:
                self.log.debug('Executor delisting worker for OGo#{0} [Process]'.format(process_id))
                del self._workers[process_id]

    def executor_create_worker(self, process_id, context_id=None, route_group=None, route_id=None):
        self.log.debug('Attempting to start/restart OGo#{0} [Process]'.format(process_id))
        if (process_id in self._workers):
            # TODO: Signal the route, maybe it wants to check for new messages?
            self.log.info('A worker already exists for OGo#{0} [Process]'.format(process_id))
            return False
        else:
            self.send(Packet('coils.workflow.executor/__null',
                             'coils.workflow.logger/log',
                             { 'process_id': process_id,
                               'category': 'debug',
                               'message': 'Creating worker.'} ) )
            # Start a new process
            s, r = multiprocessing.Pipe()
            p = multiprocessing.Process(target=start_workflow_process,
                                        args=(process_id, context_id))
            self._workers[process_id] = { 'process_id': process_id,
                                          'status':     'running',
                                          'timestamp':   time(),
                                          'context_id':  context_id,
                                          'process':     p, }
            try:
                p.start()
                p.join(0.2)
            except Exception, e:
                self.log.error('Failed to create worker for OGo#{0} [Process]'.format(process_id))
                self.log.exception(e)
                self.send( Packet( 'coils.workflow.executor/__null', 'coils.workflow.logger/log',
                                   { 'process_id': process_id,
                                     'category': 'error',
                                     'message': 'Worker creation failed.' } ) )
                del self._workers[process_id]
                return False
            else:
                self.send( Packet( 'coils.workflow.executor/__null', 'coils.workflow.logger/log',
                                   { 'process_id': process_id,
                                     'category': 'debug',
                                     'message': 'Worker started.'} ) )
                self.log.debug('Worker for OGo#{0} [Process] started.'.format(process_id))
                return True


    def do_start(self, parameter, packet):
        process_id = packet.data.get('processId')
        context_id = packet.data.get('contextId')
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'debug',
                           'message': 'Request to start.'} ))
        self.log.info('Received message to start/restart OGo#{0} [Process] with contextId#{0}'.format(process_id, context_id))
        try:
            started = self.executor_start_process(process_id, context_id)
        except Exception, e:
            self.log.warn('Unable to start OGo#{0} [Process]'.format(process_id))
            self.log.exception(e)
            self.send(Packet.Reply(packet, {'status': 500, 'text': 'ERROR'}))
        else:
            if started:
                self.log.info('Successfully started/restarted processId#{0}'.format(process_id))
                self.send(Packet.Reply(packet, { 'status': 201,
                                                 'text': 'OK; started.',
                                                 'running': 'YES',
                                                 'processId': process_id } ) )                
            else:
                self.log.info('Declined to start/restart processId#{0}'.format(process_id))
                # TODO: What would be a resonable status for this?
                self.send(Packet.Reply(packet, { 'status': 200,
                                                 'text': 'OK; declined.',
                                                 'running': 'NO',
                                                 'processId': process_id } ) )

    def do_signal(self, parameter, packet):
        # TODO: Authorize signal!
        try:
            process_id = packet.data.get('processId')
            context_id = packet.data.get('contextId')
            self.executor_restart_process(process_id, context_id)
        except Exception, e:
            self.send(Packet.Reply(packet, { 'status': 500,
                                             'text': '{0}'.format(e) } ) )
        else:
            self.send(Packet.Reply(packet, { 'status': 201,
                                             'text': 'OK' } ) )

    def do_running(self, parameter, packet):
        ''' Packet indicates the process is actively working, update the timestamp '''
        process_id = packet.data.get('processId')
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'debug',
                           'message': 'Process reported as running.'} ))
        if process_id in self._workers:
            worker = self._workers.get(process_id)
            if worker.get('timestamp') < packet.time:
                self._workers[process_id]['status'] = 'running'
                self._workers[process_id]['timestamp'] = time()
        else:
            self.log.info( 'Learned of unknown worker for processId#{0}'.format(process_id) )
            self._workers[process_id] = { 'process_id': process_id,
                                          'status':     'running',
                                          'timestamp':   time(),
                                          'context_id':  0,
                                          'process':     None }

    def do_parked(self, parameter, packet):
        ''' Parking a workflow is effectively the same as shutting down.'''
        process_id = packet.data.get('processId')
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'debug',
                           'message': 'Process reported as parked.'} ))
        if (process_id in self._workers):
            #del self._workers[process_id]
            self._workers[process_id]['status'] = 'parked'
            self.log.debug('discarding parked process {0}'.format(process_id))
        return

    def do_failure(self, parameter, packet):
        ''' When a process fails shut down the worker '''
        # TODO: Send an administrative notice?
        process_id = packet.data.get('processId')
        self.send( Packet( None, 'coils.workflow.logger/log',
                           { 'process_id': process_id,
                             'category': 'debug',
                             'message': 'Process reported as failed.'} ) )
        if process_id in self._workers:
            self._workers[process_id]['status'] = 'failed'
        # Tell the manager the process failed
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.manager/failed:{0}'.format(process_id),
                         None))
        self.executor_delist_worker(process_id)

    def do_complete(self, parameter, packet):
        ''' When a process is complete, shut down the worker '''
        process_id = packet.data.get('processId')
        # Log that we received a complete message from the worker
        self.send( Packet( 'coils.workflow.executor/__null', 'coils.workflow.logger/log',
                           { 'process_id': process_id,
                             'category': 'debug',
                             'message': 'Process reported as completed.'} ) )
        if process_id in self._workers:
            self._workers[process_id]['status'] = 'complete'
            self.log.debug('discarding completed process {0}'.format(process_id))
        # Tell the manager that this process is completed
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.manager/completed:{0}'.format(process_id),
                         None))
        self.executor_delist_worker(process_id)

    def do_ticktock(self, parameter, packet):
        self.log.info('TickTock: {0} active workers'.format(len(self._workers)))
        if len(self._workers):
            self.send(Packet('coils.workflow.executor/__null',
                            'coils.workflow.executor/verify_workers',
                            None ))

    def do_is_running(self, parameter, packet):
        process_id = int(parameter)
        self.log.info('Process status check for OGo#{0} [Process] by {1}'.format(process_id, packet.source))
        if self.executor_verify_worker(process_id):
            self.send(Packet.Reply(packet, { 'status': 200,
                                             'text': 'Worker verified by executor',
                                             'running': 'YES',
                                             'processId': process_id } ) )
        else:
            self.send(Packet.Reply(packet, { 'status': 200,
                                             'text': 'Executor cannot verify worker for process',
                                             'running': 'NO',
                                             'processId': process_id  } ) )

    def do_kill(self, parameter, packet):
        process_id = int(parameter)
        signal = packet.data.get('signal', 15)
        self.send(Packet('coils.workflow.executor/__null',
                         'coils.workflow.logger/log',
                         { 'process_id': process_id,
                           'category': 'control',
                           'message': 'Request to kill.'} ))
        if (process_id in self._workers):
            if (signal == 9):
                # hard kill
                # TODO: implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            elif (signal == 15):
                self.send(Packet('coils.workflow.executor/__null',
                                 'coils.workflow.process.{0}/kill:{0}'.format(process_id),
                                 None))
                self.send(Packet.Reply(packet, {'status': 201, 'text': 'OK'}))
            elif (signal == 1):
                # Reload ?
                # TODO Implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            elif (signal == 17):
                # Suspend (Park!)
                # TODO Implement
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Not Implemented'}))
            else:
                self.send(Packet.Reply(packet, {'status': 500, 'text': 'Unknown kill signal'}))
        else:
            self.send(Packet.Reply(packet, {'status': 404, 'text': 'OK', 'running': 'No worker for PID' }))

    def do_verify_workers(self, parameter, packet):
        purge = [ ]
        
        self.log.info('Worker status verification requested by {0}'.format(packet.source))
        
        for pid in self._workers:
            if not self.executor_verify_worker(pid):
                purge.append(pid)
                
        self.log.info('Workder verification complete; {0} workers will be discarded'.format(len(purge)))
        
        if purge:
            for pid in purge:
                self.log.info('Discarding worker for OGo#{0} [Process]'.format(pid))
                del self._workers[pid]
