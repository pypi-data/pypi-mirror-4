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
# THE SOFTWARE.f
#
import sys, logging, pickle, re
from os                    import nice as os_priority
from lxml                  import etree
from datetime              import datetime
from coils.core            import *
from exception             import NoActionException, \
                                   UnknownActionException, \
                                   NoSuchMessageException
from coils.logic.workflow  import ActionMapper

#
# TODO: Clean-up!  Works great, but is getting a bit spider-webby.
#

def filename_for_process_code(process):
    return 'wf/p/{0}.{1}.cpm'.format(process.object_id, process.version)

class Process(Service):
    __auto_dispatch__  = True
    __is_worker__      = True
    __TimeOut__        = 0.1
    __DebugOn__        = None
    __AMQ_Expiration__ = 2700000 # Expiration on a process queue is 45 minutes

    def __init__(self, p, c):
        self._process_id = p
        self._context_id = c
        Service.__init__(self)
        if (Process.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            Process.__DebugOn__ = sd.bool_for_default('OIEProcessDebugEnabled')

    @property
    def debug(self):
        return Process.__DebugOn__

    def setup(self, silent=True):
        self.__service__ = 'coils.workflow.process.{0}'.format(self._process_id)
        Service.setup(self, silent=silent)

    def decrease_priority(self):
        try:
            os_priority(20)
        except Exception, e:
            self.log_message('os', 'Unable to decrease priority of workflow worker process.')
            self.log.exception(e)

    def prepare(self):
        Service.prepare(self)
        self._route_name = None
        self._process    = None
        self._ctx        = None
        self._killed     = False
        self.iteration   = 0

        if (Process.__DebugOn__):
            self.log.info('Workflow process debugging enabled (OIEProcessDebugEnabled:YES)')
        else:
            self.log.info('Workflow process debugging disabled (OIEProcessDebugEnabled:NO)')

        # Create context
        try:
            if (self._context_id == 8999):
                self._ctx = NetworkContext(broker=self._broker)
                self.log.info('Process using the network context')
                self.send(Packet(None, 'coils.workflow.logger/log',
                                 { 'process_id': self._process_id,
                                   'stanza': None,
                                   'message': 'Process using the network context' } ) )
            elif (self._context_id == 10000):
                self._ctx = AdministrativeContext(broker=self._broker)
                self.log.info('Process using the administrative context')
                self.send(Packet(None, 'coils.workflow.logger/log',
                                 { 'process_id': self._process_id,
                                   'stanza': None,
                                   'message': 'Process using the administrative context' } ) )
            elif (self._context_id == 0):
                self._ctx = AnonymousContext(broker=self._broker)
                self.log.info('Process using the anonymous context')
                self.send(Packet(None, 'coils.workflow.logger/log',
                                 { 'process_id': self._process_id,
                                   'stanza': None,
                                   'message': 'Process using the anonymous context' } ) )
            else:
                self._ctx = AssumedContext(self._context_id, broker=self._broker)
                self.log.info('Process using the assumed contextId#{0}'.format(self._context_id))
                self.send(Packet(None, 'coils.workflow.logger/log',
                                 { 'process_id': self._process_id,
                                   'stanza': None,
                                   'message': 'Process using assumed contextId#{0}'.format(self._context_id) } ) )
        except Exception, e:
            # TODO: Log what context we were trying to create
            message = traceback.format_exc()
            subject = 'Workflow process failed to allocate context for processId#{0}'.format(self._process_id)
            self.log.error(subject)
            self.log.exception(e)
            self.send_administrative_notice(subject=subject,
                                message=message,
                                urgency=8,
                                category='workflow',
                                attachments=[])
            #TODO: Send a message to the manager that we have failed!

        # Let's go!
        # Load process
        self._process = self._ctx.run_command('process::get', id=self._process_id,
                                                              access_check=False)
        if (self._process is None):
            self.send(Packet('{0}/__null'.format(self.__service__),
                 'coils.workflow.executor/failure',
                 { 'processId': self._process_id }))
            self.shutdown()
        self.load_state()
        self._process.started = self._ctx.get_utctime()
        self._process.state = 'R'
        self._process.parked  = None
        self.save_state()
        self.log_message('started', 'Process {0} started'.format(self._process.object_id))
        self._ctx.commit()
        self.send(Packet('{0}/__null'.format(self.__service__),
                         'coils.workflow.executor/running',
                         { 'processId': self._process_id }))
        self.decrease_priority()
        self.send(Packet(None,
                         'coils.workflow.logger/log',
                         { 'process_id': self._process.object_id,
                           'stanza': None,
                           'message': 'Prepared'} ))

# State

    def load_state(self):
        self.send(Packet(None,
                         'coils.workflow.logger/log',
                         { 'process_id': self._process_id,
                           'stanza': None,
                           'message': 'Loading state: {0}'.format(filename_for_process_code(self._process))} ))
        source = BLOBManager.Open(filename_for_process_code(self._process), 'rb', encoding='binary')
        if (source is None):
            self.send(Packet(None,
                             'coils.workflow.logger/log',
                             { 'process_id': self._process_id,
                               'stanza': None,
                               'message': 'Unable to load state' } ))
            self.die()
        else:
            self._cpm = pickle.load(source)
            BLOBManager.Close(source)
            self.send(Packet(None,
                             'coils.workflow.logger/log',
                             { 'process_id': self._process_id,
                               'stanza': None,
                               'message': 'State loaded' } ))
            self._park = False
            self._complete = False

    def save_state(self):
        try:
            self._process.version = self._process.version + 1
            self.log_message('state', 'Saving process state to {0}'.format(filename_for_process_code(self._process)))
            source = BLOBManager.Create(filename_for_process_code(self._process), encoding='binary')
            pickle.dump(self._cpm, source)
            BLOBManager.Close(source)
            self.log_message('state', 'Save complete')
            self._ctx.commit()
        except Exception as e:
            self.log.exception(e)
            self.log_message('exception', 'An exception saving state')
            return False
        else:
            return True

# Message acquisition and action execution

    def get_message(self, label):
        message = self._ctx.run_command('message::get', process=self._process,
                                                        scope=self.stack,
                                                        label=label)
        if (message is None):
            self.log_message('error', 'No such message as {0} in proccess {1} with scope {2}'.\
                format(label, self._process.object_id, ','.join(self.stack)))
            raise NoSuchMessageException('No such message as {0} in process.'.format(label))
        return message

    def run_stanza(self, uuid):

        stanza = self._cpm[uuid]
        self.send(Packet('{0}/__null'.format(self.__service__),
                         'coils.workflow.executor/running',
                         { 'processId': self._process_id }))



        if (stanza.get('control') is None):
            # This is a normal non-control action
            # 1.) Lookup Action
            _action_name = stanza.get('params', { }).get('activityName', None)
            _description = stanza.get('params', { }).get('description', u'No description.')
            if (_action_name is None):
                raise NoActionException()
            self.send(Packet(None,
                             'coils.workflow.logger/log',
                             { 'process_id': self._process.object_id,
                               'stanza': uuid,
                               'category': 'start',
                               'message': _action_name } ) )
            _action = ActionMapper.get_action(_action_name)
            if (_action is None):
                self.log_message('error', 'No support for process action {0}'.format(_action_name))
                raise UnknownActionException('No support for process action {0}'.format(_action_name))
            # 2.) Get Input Message
            # We want to support no-input actions, way more efficient than knowningly
            # looking up a message we are not going to use.
            _input = stanza.get('input')
            if (_input is None):
                _message = None
            else:
                #TODO: What about the specified format?
                _message = self.get_message(_input.get('label'))
            # 3.) Run Command
            # TODO: Test that _output has a format and label key
            label = None
            if (stanza['output'] is not None):
                if ('label' in stanza['output']):
                    label = stanza['output']['label']
            self.send(Packet(None,
                             'coils.workflow.logger/log',
                             { 'process_id': self._process.object_id,
                               'stanza': uuid,
                               'category': 'debug',
                               'message': 'logic command is "{0}"'.format(_action) } ))
            (self._continue, self._proceed) = self._ctx.run_command(_action,
                                                                    input=_message,
                                                                    process=self._process,
                                                                    uuid=uuid,
                                                                    scope=self.stack,
                                                                    state=self._cpm['__state__'],
                                                                    label=label,
                                                                    parameters=stanza.get('params'))
            if (self._continue):
                if (self._proceed):
                    self._cpm['__next__'] = stanza.get('next')
            else:
                self._park = True
            return _action_name, _description
        else:
            self._continue = True
            self._proceed = True
            self._park = False
            # Control action!
            self.send(Packet(None,
                             'coils.workflow.logger/log',
                             { 'process_id': self._process.object_id,
                               'stanza': uuid,
                               'category': 'start',
                               'message': 'control "{0}"'.format(stanza.get('control')) } ))
            if (stanza.get('control') == 'start'):
                self._cpm['__next__'] = stanza.get('next')
                self.send(Packet(None,
                                 'coils.workflow.logger/log',
                                 { 'process_id': self._process.object_id,
                                   'stanza': uuid,
                                   'category': 'debug',
                                   'message': 'first action will be "{0}"'.format(self._cpm['__next__'])} ))
            elif (stanza.get('control') == 'foreach'):
                self._flow_foreach(uuid)
            elif (stanza.get('control') == 'switch'):
                self._flow_switch(uuid)
            elif (stanza.get('control') == 'while'):
                self._flow_while(uuid, stanza)
            elif (stanza.get('control') == 'until'):
                self._flow_until(uuid)
            else:
                self.log_message('error', 'Unsupported control action: {0}'.format(stanza.get('control')))
                raise CoilsException('Unsupported control action: {0}'.format(stanza.get('control')))
            return stanza.get('control'), 'No description'


# Flow Control

    # Foreach
    def _flow_foreach(self, uuid):
        stanza = self._cpm[uuid]
        node_list = stanza.get('nodes', None)
        if (node_list is None):
            message = self.get_message(stanza.get('input').get('label'))
            rfile = self._ctx.run_command('message::get-handle', object=message)
            doc = etree.parse(rfile)
            BLOBManager.Close(rfile)
            # TODO: Get namespaces from the document!
            namespaces = { 'dsml': 'http://www.dsml.org/DSML' }
            result = doc.xpath(stanza.get('params').get('xpath'), namespaces=namespaces)
            if (isinstance(result, list)):
                self._cpm['__next__'] = uuid
                stanza['nodes'] = [ ]
                stanza['count'] = 0
                for x in result:
                    if (hasattr(x, 'is_text')):
                        # TODO: There must be a better way to detect IS TEXT!
                        stanza['nodes'].append(str(x))
                    else:
                        stanza['nodes'].append(etree.tostring(x))
                if (self.debug):
                    self.log_message('foreach', 'foreach initialized; scope {0} w/{1} nodes'.\
                        format(self.stack_tip, len(stanza.get('nodes'))))
            else:
                if (self.debug):
                    self.log_message('foreach', 'foreach shorting out, nothing to iterate.')
        else:
            if (self.debug):
                self.log_message('foreach', 'resuming foreach for listed nodes')
            node_list = stanza['nodes']
            if (len(node_list) > 0):
                self.stack.append(uuid)
                stanza['count'] = stanza['count'] + 1
                if (self.debug):
                    self.log_message('foreach', 'foreach iteration; scope:{0} count:{1}'.format(self.stack_tip, stanza['count']))
                node = node_list.pop(0)
                if ('current' in stanza):
                    message = self._ctx.run_command('message::get', uuid=stanza['current'])
                    self._ctx.run_command('message::set', object=message, data=node)
                else:
                    message = self._ctx.run_command('message::new', process=self._process,
                                                                    data=node,
                                                                    scope=self.stack_tip,
                                                                    mimetype='application/x-opengroupware-message-xml',
                                                                    label='current')
                    stanza['current'] = message.uuid
                self._cpm['__next__'] = stanza.get('branch')
                # Continue execution, but do not proceed
            else:
                # Node list exhausted, proceed
                if (self.debug):
                    self.log_message('foreach', 'foreach node list exhausted; scope:{0}'.format(self.stack_tip))
                self._cpm['__next__'] = stanza.get('next')
        return True, True

    # Switch
    def _flow_switch(self, uuid):
        """ {'control': 'switch', 'name': u'switchActivity',
             'default': {'action': u'000000000006', 'id': None},
             'next': u'000000000005',
             'output': None,
             'input': None,
             'cases': [{'action': u'000000000006', 'expression': u"$object_name;==''", 'id': u'1'}],
             'previous': u'000000000005'} """
             
        stanza = self._cpm[uuid]
        
        complete = True
        
        if stanza.get('compelete', False):
            
            # We've already performed the switch, and fallen back out of that
            # scope back into the flow control operator.  So proceed to the 
            # action following the switch clause
            self._cpm['__next__'] = stanza.get('next')
            
            self.log_message( 'switch', 
                              'resuming flow control from child scope',
                              debug = True )
            
        else:
            
            # Mark the switch as executed before we go anywhere else
            # Now when we fall back out of the subordinate scope the
            # process will proceed to the action following the switch.
            self._cpm[uuid]['complete'] = True
            
            for case in stanza['cases']:
                expression = case.get('expression')
                if self._eval_expression(expression):
                    self._cpm['__next__'] = case.get('action')
                    self.log_message( 'switch', 
                                      'evaluation for jump to "{0}" is True'.format(self._cpm['__next__']),
                                      debug = True )
                    break
                else:
                    self.log_message( 'switch', 
                                      'evaluation for jump to "{0}" is False"'.format( self._cpm[ '__next__' ] ),
                                      debug = True )                    
            else:
                self.log_message( 'switch', 'no case evaluated to True', debug = True )
                next = stanza.get('default', {}).get('action', None)
                if next:
                    self.log_message( 'switch', 
                                      'falling through to default case action "{0}"'.format(next),
                                      debug = True )
                else:
                    next = stanza.get('next')
                    self.log_message( 'switch', 
                                      'no qualifying case in switch progessing to action "{0}"'.format(next),
                                      debug = True )
                self._cpm['__next__'] = next
                
        return True, True

    def _eval_expression(self, expression):
        labels = set(re.findall('\$__[A-z]*__;', expression))
        for label in labels:
            if (label == '$__DATE__;'):
                expression = expression.replace(label, "'{0}'".format(datetime.now().strftime('%Y%m%d')))
            elif (label == '$__DATETIME__;'):
                expression = expression.replace(label, "'{0}'".format(datetime.now().strftime('%Y%m%dT%H:%M')))
            elif (label == '$__PID__;'):
                expression = expression.replace(label, "'{0}'".format(str(self._process.object_id)))
            elif (label[0:9] == '$__XATTR_'):
                propname = label[9:-3].lower()
                prop = self._ctx.property_manager.get_property(self._process,
                                                               'http://www.opengroupware.us/oie',
                                                               'xattr_{0}'.format(propname))
                if (prop is not None):
                    value = str(prop.get_value())
                    expression = expression.replace(label, "'{0}'".format(value))
                else:
                    self.log.debug('Encountered unknown xattr reference {0}'.format(propname))
                    expression = expression.replace(label, '')
            else:
                self.log_message( 'evaluation', 
                                  'Encountered unknown {0} content alias'.format(label),
                                  debug = True )
        labels = set(re.findall('\$[A-z]*;', expression))
        if (len(labels) > 0):
            for label in labels:
                self.log_message( 'evaluation', 
                                  'Retrieving text for label {0}'.format(label),
                                  debug = True )
                try:
                    data = self._ctx.run_command('message::get-text', process=self._process,
                                                                      scope=self.stack,
                                                                      label=label[:-1][1:])
                except Exception, e:
                    self.log.exception(e)
                    self.log_message('error', 'Exception retrieving text for label {0}'.format(label))
                    raise e
                expression = expression.replace(label, "'{0}'".format(data))
                
        result = eval(expression)
        if self.debug:
            self.log_message('evaluation', 'Evaluation of expression "{0}" returned {1}'.format(expression, result))
        return result

    # While: Look until false
    def _flow_while(self, uuid):
        stanza = self._cpm[uuid]
        self.log_message('while', 'Unsupported control action: while')
        raise NotImplementedException('Flow control structure "while" not implemented.')

    # Until: Loop until true
    def _flow_until(self, uuid):
        stanza = self._cpm[uuid]
        self.log_message('until', 'Unsupported control action: until')
        raise NotImplementedException('Flow control structure "while" not implemented.')

# Logging & Error Handling (Exception Route)

    def log_message(self, action, message, debug=False):
        if (len(action) > 0):
            message = '{0}: {1}'.format(action, message)
        self.log.debug(message)
        if debug and not self.debug:
            return
        self.send(Packet(None,
                         'coils.workflow.logger/log',
                         { 'process_id': self._process.object_id,
                           'message': message } ))

    def run_exception_context(self, message):
        # TODO: Implement
        self.send(Packet(None,
                         'coils.workflow.logger/log',
                         { 'process_id': self._process.object_id,
                           'message': 'Exception condition!' } ))
        self.log_message('exception', message)
        output = self._ctx.run_command('message::new', process=self._process,
                                                       label='error',
                                                       data=message)
        action_uuid = self._cpm.get('__error__', None)
        self.send(Packet('{0}/__null'.format(self.__service__),
                         'coils.workflow.executor/failure',
                         {'processId': self._process_id}))
        self._process.output_message = output.uuid
        output = None
        self._process.completed = self._ctx.get_utctime()
        self.log_message('exception', 'Failure time is {0}'.format(self._process.completed))
        self._process.state = 'F'
        self._ctx.commit()
        action_uuid = self._cpm.get('__error__', None)
        if (action_uuid is None):
            self.log_message('exception', 'No exception path found in route.')
            self._continue = False
        else:
            self._continue = True
        while (self._continue):
            try:
                self.run_stanza(action_uuid)
                if (self._proceed):
                    action_uuid = self._cpm.get('__next__', None)
                    if (action_uuid is None):
                        self._continue = False
            except Exception, e:
                self.log_message('exception', 'An exception occurred in exception stanza {0} of process {1}'.format(action_uuid, self._process_id))
                self.log.exception(e)
                self._continue = False
            else:
                self._ctx.commit()
                self.save_state()
        self.log_message('failed', 'Process {0} failed'.format(self._process.object_id))
        self._ctx.commit()
        self.shutdown()

# Run

    def prepare_state(self):
        # _cpm (Coils Process Markup [a pickle file] is loaded by load_state()
        # which is invoked in prepare()
        self._continue = True
        if ('__namespace__' in self._cpm):
            # Route is starting, otherwise __namespace__ would not be present
            self._route_name = self._cpm.get('__namespace__')
            self._cpm = self._cpm.get(self._route_name)
            self._cpm['__state__'] = { }
            self._cpm['__stack__'] = [ ]
            self._cpm['__next__']  = self._cpm.get('__start__', None)
            self._proceed  = True
            self._continue = True
            self.save_state()

    def work(self):
        if (self.iteration == 0):
            self.prepare_state()
        if (self.killed):
            self.run_exception_context('Process termination requested via Administrative action.')
        action_uuid = self.next_stanza_uuid
        # If there is no action to perform we assume the route is complete
        if (action_uuid):
            self.iteration = self.iteration + 1
            try:
                action_name, description = self.run_stanza(action_uuid)
                self.send(Packet(None,
                                 'coils.workflow.logger/log',
                                 { 'process_id': self._process.object_id,
                                   'stanza': action_uuid,
                                   'category': 'complete',
                                   'message': description } ))
            except Exception, e:
                self.log.exception(e)
                message = traceback.format_exc()
                self.send(Packet(None,
                                 'coils.workflow.logger/log',
                                 { 'process_id': self._process.object_id,
                                   'stanza': action_uuid,
                                   'category': 'error',
                                   'message': 'exception in stanza {0}\n{1}'.format(action_uuid, message) } ))
                self._ctx.rollback()
                self.log.error('An exception occurred in stanza {0} of process {1}'.format(action_uuid, self._process_id))
                # TODO: log event in process entities event log
                self.run_exception_context(message)
            else:
                self.save_state()
        if (self._park):
            self._do_park()
        elif (self._complete):
            # Route complete
            self._do_complete()

    def _do_park(self):
        # Process parked
        self.send(Packet(None,
                         'coils.workflow.logger/log',
                         { 'process_id': self._process.object_id,
                           'message': 'Parking' } ))
        self.send(Packet('{0}/__null'.format(self.__service__),
                         'coils.workflow.executor/parked',
                         { 'processId': self._process_id,
                           'status':    201,
                           'message':   'OK' }))
        self._process.parked = self._ctx.get_utctime()
        self._process.state = 'P'
        self.log_message('parked', 'Process {0} parked'.format(self._process.object_id))
        self.save_state()
        self.shutdown()

    def _do_complete(self):
        # Process complete
        self.send(Packet(None,
                         'coils.workflow.logger/log',
                         { 'process_id': self._process.object_id,
                           'message': 'Completing' } ))
        # 1.) Mark output message
        start_uuid = self._cpm.get('__start__')
        output_label = self._cpm.get(start_uuid).get('output', {}).get('label', 'OutputMessage')
        self.log_message('complete', 'Output message is {0} from stanza {1}'.format(output_label, start_uuid))
        message = self._ctx.run_command('message::get', process=self._process,
                                                        label=output_label)
        if (message is None):
            self.log_message('complete', 'Specified OutputMessage not found in global scope, using input message.')
            message = self._ctx.run_command('process::get-input-message', process=self._process)
        self._process.output_message = message.uuid
        self.log_message('complete', 'Output message is {0}'.format(self._process.output_message))
        # 2.) Bump process info
        self._process.completed = self._ctx.get_utctime()
        self.log_message('complete', 'Completed time is {0}'.format(self._process.completed))
        self._process.state = 'C'
        # 3.) Log completion
        self.log_message('complete', 'Process {0} completed'.format(self._process.object_id))
        # 4.) Commit!
        self.save_state()
        self.log_message('complete', 'Process completion committed')
        # 5.) Send someone a complete message
        self.send(Packet('{0}/__null'.format(self.__service__),
                         'coils.workflow.executor/complete',
                         { 'processId': self._process_id,
                           'status':    201,
                           'message':   'OK' }))
        self.shutdown()

    def do_kill(self, parameter, packet):
        if (int(parameter) == self._process.object_id):
            self.send(Packet.Reply(packet, {'status': 200, 'text': 'OK'}))
            self.kill()
        else:
            self.send(Packet.Reply(packet, {'status': 404, 'text': 'Incorrect PID'}))

# State

    @property
    def state(self):
        return self._cpm['__state__']

    @property
    def stack(self):
        return self._cpm['__stack__']

    @property
    def stack_tip(self):
        if (len(self.stack) == 0):
            return None
        return self.stack[-1]

    def pop_stack(self):
        if (self.debug):
            self.log_message('stack', 'stack reduced')
        return self.stack.pop()

    def die(self):
        self._process.completed = self._ctx.get_utctime()
        self._process.state = 'F'
        self._ctx.commit()
        self.send(Packet(None,
                         'coils.workflow.executor/failure',
                         { 'processId': self._process_id }))
        self.shutdown()

    @property
    def next_stanza_uuid(self):
        # Returns the next UUID to be processed
        # NOTE: This may be the same UUID as previously executed in the case of
        #       an iteration such as foreach, until, and while.
        action_uuid = self._cpm.get('__next__', None)
        # If __next__ is None that means we have reached the end of a scope, which
        # may or may not be the outermost scope.  So pop the stack in order to
        # resume the next-outer scope.
        if ((action_uuid is None) and (len(self.stack) > 0)):
            action_uuid = self.pop_stack()
        if (action_uuid is None):
            self._complete = True
        return action_uuid

    @property
    def _proceed(self):
        return self._cpm['__proceed__']

    @_proceed.setter
    def _proceed(self, value):
        if (value):
            self._cpm['__proceed__'] = True
        else:
            self._cpm['__proceed__'] = False

    @property
    def _continue(self):
        return self._cpm['__continue__']

    @_continue.setter
    def _continue(self, value):
        if (value):
            self._cpm['__continue__'] = True
        else:
            self._cpm['__continue__'] = False

    @property
    def _next(self):
        return self._cpm.get('__next__', None)

    @_next.setter
    def _next(self, value):
        self._cpm['__next__'] = value

    def kill(self):
        self._killed = True

    @property
    def killed(self):
        if (self._killed):
            return True
        else:
            return False
