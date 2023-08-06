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
#
import logging
from coils.core      import NotImplementedException, CoilsException
from xml.sax.handler import ContentHandler

BPML_BOOTSTRAP_MODE  = 0
BPML_PACKAGE_MODE    = 1
BPML_PROCESS_MODE    = 2
BPML_CONTEXT_MODE    = 3
BPML_ACTION_MODE     = 4
BPML_INPUT_MODE      = 5
BPML_EXTENSION_MODE  = 6
BPML_OUTPUT_MODE     = 7
BPML_SOURCE_MODE     = 8
BPML_EXCEPTION_MODE  = 9
BPML_EVENT_MODE      = 10
BPML_FAULTS_MODE     = 11
BPML_ATTRIBUTES_MODE = 12
BPML_FOREACH_MODE    = 13
BPML_SWITCH_MODE     = 14   # Not yet implemented
BPML_CASE_MODE       = 15   # Not yet implemented
BPML_UNTIL_MODE      = 16   # Not yet implemented
BPML_WHILE_MODE      = 17   # Not yet implemented
BPML_SEQUENCE_MODE   = 18   # Not yet implemented
BPML_CONDITION_MODE  = 19   # Not yet implemented
BPML_DEFAULT_MODE    = 20   # Not yet implemented
BPML_UNDEFINED_MODE  = 21   # Not yet implemented

# TODO: We need to support parsing complex actions
#  foreach [id= select= formatter= ]
#    source propert={message label} xpath=""
#    actions....
#    context [useless]
#      faults [useless]
#  - foreach creates an output message of "current"
#  - what happens if foreach actions are nested, what happens to "current"?
#
#  switch [id= ]
#    case [id = ]
#      condition [expression= ] example: <condition expression="$object_name;==''"/>
#        - where ${message_label}; relates to content of the specified message
#        - is this a job for eval() ???
#      context [useless]
#        faults [useless]
#      actions....
#    default [id= ]
#      <condition/>
#      context [useless]
#        faults [useless]
#      actions....



class BPMLSAXHandler(ContentHandler):

    def __init__(self):
        ContentHandler.__init__(self)
        self.mode = [ BPML_BOOTSTRAP_MODE ]
        self.actions = { }
        self.result = { }
        self.log = logging.getLogger('xml:bpml')
        self._io_flip = True
        self._stack = [ ]


    @property
    def stack_tip(self):
        if len(self._stack) > 0:
            return self._stack[-1]
        return None

    def pop_stack(self):
        if len(self._stack) > 0:
            return self._stack.pop()
        return None

    @property
    def current_mode(self):
        return self.mode[-1]

    def startElement(self, name, attrs):
        if (name == 'package' and self.mode[-1] == BPML_BOOTSTRAP_MODE):
            self.mode.append(BPML_PACKAGE_MODE)
            self.current_uuid = None
            self.previous_uuid = None
            self.context_uuid = None
            self._stack = []
            self.result['__namespace__'] = attrs.get('targetNamespace')
        elif (name == 'process' and self.current_mode == BPML_PACKAGE_MODE):
            # Entering the process section of a package
            self.mode.append(BPML_PROCESS_MODE)
            self.process_name = attrs.get('name', None)
        elif (name == 'event' and self.current_mode == BPML_PROCESS_MODE):
            self.mode.append(BPML_EVENT_MODE)
        elif (name == 'context'):
            # We do nothing with contexts.  We simply enter the context mode
            # so we can exit it again at the end of the section
            self.mode.append(BPML_CONTEXT_MODE)
            
        elif (name == 'action'):
            if (self.current_mode in [ BPML_CONTEXT_MODE, BPML_PROCESS_MODE ]):
                # Clear the previous action reference if crossing a context or
                # process boundry (Will this ever happen?_
                self.previous_uuid = None
                
            self.current_uuid  = attrs.get('id', None)
            
            #self.log.debug('Action id#{0}'.format(self.current_uuid))
            # Scope;  append id of current action
            
            if (self.previous_uuid == None):
                if (self.current_mode == BPML_EXCEPTION_MODE):
                    self.actions['__error__'] = self.current_uuid
                elif (self.current_mode == BPML_PROCESS_MODE):
                    self.actions['__start__'] = self.current_uuid
                    self._io_flip = False
            elif (self.current_mode == BPML_FOREACH_MODE and
                  self.stack_tip == self.previous_uuid):
                self.actions[self.previous_uuid]['branch'] = self.current_uuid
                self._io_flip = True
            elif (self.current_mode == BPML_CASE_MODE and
                  self.stack_tip == self.previous_uuid):
                self.actions[self.previous_uuid]['cases'][-1]['action'] = self.current_uuid
                self._io_flip = True
            elif (self.current_mode == BPML_DEFAULT_MODE and
                  self.stack_tip == self.previous_uuid):
                self.actions[self.stack_tip]['default']['action'] = self.current_uuid
                self._io_flip = True
            else:
                self.actions[self.previous_uuid]['next'] = self.current_uuid
                self._io_flip = True
            if (self.current_mode == BPML_EXCEPTION_MODE):
                self.actions[self.current_uuid] = { 'previous': None,
                                                    'next':     None,
                                                    'control':  None,
                                                    'input':    None,
                                                    'output':   None,
                                                    'params':   { },
                                                    'name':     attrs.get('name') }
            elif (self.previous_uuid is None):
                self.actions[self.current_uuid] = { 'previous': None,
                                                    'next':     None,
                                                    'control':  'start',
                                                    'input':    None,
                                                    'output':   None,
                                                    'params':   { },
                                                    'name':     attrs.get('name') }
            else:
                self.actions[self.current_uuid] = { 'previous': self.previous_uuid,
                                                    'next':     None,
                                                    'control':  None,
                                                    'input':    None,
                                                    'output':   None,
                                                    'params':   { },
                                                    'name':     attrs.get('name') }
            self.mode.append(BPML_ACTION_MODE)
            
            if self.previous_uuid:
                if 'tails' in self.actions[self.previous_uuid]:
                    #print 'previous uuid of {0} has tails'.format(self.previous_uuid)
                    for tail in self.actions[self.previous_uuid]['tails']:
                        #print 'setting next of {0} to {1}'.format(tail, self.current_uuid)
                        self.actions[tail]['next'] = self.current_uuid

            
            self.previous_uuid = self.current_uuid
            
        elif (name == 'faults'):
            self.mode.append(BPML_FAULTS_MODE)
        elif (name == 'attributes'):
            self.mode.append(BPML_ATTRIBUTES_MODE)
        elif (name == 'input' and self.mode[-1] == BPML_ACTION_MODE):

            self.mode.append(BPML_INPUT_MODE)
            if (self._io_flip):
                self.actions[self.current_uuid]['output'] = { 'label': attrs.get('property'),
                                                             'format': attrs.get('formatter') }
            else:
                self.actions[self.current_uuid]['input'] = { 'label': attrs.get('property'),
                                                             'format': attrs.get('formatter') }

        elif (name == 'output' and self.current_mode == BPML_ACTION_MODE):
            self.mode.append(BPML_OUTPUT_MODE)
        elif (name == 'extension' and self.current_mode == BPML_ATTRIBUTES_MODE):
            # Accumulatng extenstion values from an actions attributes section
            # These are the parameters used to control command execution
            self.mode.append(BPML_EXTENSION_MODE)
            self.name = attrs.get('name')
        elif (name == 'source' and self.current_mode in (BPML_OUTPUT_MODE, BPML_FOREACH_MODE)):
            # Encountered a source tag - source is only relevent in standard actions and
            # in foreach iterations.  Switch constructs do not process an input message
            # TODO: What about: UNTIL & WHILE ?
            self.mode.append(BPML_SOURCE_MODE)
            if (self._io_flip):
                self.actions[self.current_uuid]['input'] = { 'label': attrs.get('property'),
                                                            'format': None }
            else:
                self.actions[self.current_uuid]['output'] = { 'label': attrs.get('property'),
                                                              'format': None }
        elif (name == 'exception' and self.current_mode == BPML_CONTEXT_MODE):
            self.mode.append(BPML_EXCEPTION_MODE)
        elif (name == 'foreach'):
            # Enter a foreach control structure
            self.mode.append(BPML_FOREACH_MODE)
            self.current_uuid  = attrs.get('id', None)
            # Create a new scope for the iteration
            self._stack.append(self.current_uuid)
            self.actions[self.current_uuid] = { 'previous': self.previous_uuid,
                                                'control':  'foreach',
                                                'branch':   None,
                                                'next':     None,
                                                'input':    None,
                                                'output':   None,
                                                'params':   { 'xpath': attrs.get('select') },
                                                'name':     attrs.get('name') }
            self.actions[self.previous_uuid]['next'] = self.current_uuid
            self.previous_uuid = self.current_uuid
        elif (name == 'switch'):
            # Enter a switch control structure
            self.current_uuid  = attrs.get('id', None)
            #self.log.debug('Switch id#{0}'.format(self.current_uuid))
            if (self.current_mode == BPML_FOREACH_MODE):
                self.actions[self.previous_uuid]['branch'] = self.current_uuid
            self.mode.append(BPML_SWITCH_MODE)
            # Create a new scope for the switch branches
            self._stack.append(self.current_uuid)
            self.actions[self.current_uuid] = { 'previous': self.previous_uuid,
                                                'control':  'switch',
                                                'next':     None,
                                                'input':    None,
                                                'output':   None,
                                                'tails':    [ ],
                                                'cases':    [ ],
                                                'name':     attrs.get('name') }
            if (self.previous_uuid is not None):
                self.actions[self.previous_uuid]['next'] = self.current_uuid
            self.previous_uuid = self.current_uuid
        elif (name == 'case' and self.current_mode == BPML_SWITCH_MODE):
            # Entering a case within a switch control structure
            self.mode.append(BPML_CASE_MODE)
            self.current_case = attrs.get('id')
            #print 'enter case', self.current_uuid, self.previous_uuid
            #self.log.debug('Switch case id#{0}'.format(self.current_case))
        elif (name == 'condition' and self.current_mode == BPML_CASE_MODE):
            # Set the condition for the current case.  This is held in the "expresses"
            # attribute of the element.  The condition will have no CTEXT so one this
            # is taken we expect to immediately drop out of condition mode and back
            # into case.
            # TODO: Can a case [with a condition, not default] be empty?
            # TODO: It looks like we are requiring the condition to proceed the
            #        actions in the case.  This is not required by spec, we should
            #        fix ths requirement.
            self.mode.append(BPML_CONDITION_MODE)
            self.actions[self.current_uuid]['cases'].append({ 'expression': attrs.get('expression'),
                                                              'id':         self.current_case,
                                                              'action':     None  })
        elif (name == 'condition' and self.current_mode == BPML_DEFAULT_MODE):
            # We enter the condition of a default clause (in a switch statement) only
            # so we can leave it again.  There will never be anything here - it is a default.
            self.mode.append(BPML_CONDITION_MODE)
        elif (name == 'default' and self.current_mode == BPML_SWITCH_MODE):
            # Entering the default stanza of a switch, all switches will have a default
            # even if empty.  The action key of the default clause will remain None in this
            # case - the Workflow executor should ignore it.
            #print 'enter default', self.current_uuid, self.previous_uuid
            self.mode.append(BPML_DEFAULT_MODE)
            self.current_case = attrs.get('id')
            self.actions[self.previous_uuid]['default'] = { 'id':       self.current_case,
                                                            'action':   None  }
        else:
            self.mode.append(BPML_UNDEFINED_MODE)
            self.log.warn('Unprocessed start of element {0}'.format(name))

    def endElement(self, name):
        
        if (name == 'process'):
            self.result[self.process_name] =  self.actions
            self.actions = { }
            #self.log.debug('Process {0} markup closed.'.format(self.process_name))
            
        elif (name in ['case', 'default' ]):
            # Exiting a case or default switch context.  Revert the process
            # execution back to the switch.
            self.previous_uuid = self.stack_tip
            self.current_case = None
            #print 'end case/default', self.current_uuid, self.previous_uuid
            #self.actions[self.current_uuid]['next'] = None
            self.actions[self.previous_uuid]['tails'].append(self.last_action)
            #self.previous_uuid = None
            
        elif (name in [ 'foreach', 'switch', 'sequence', 'until', 'while' ]):
            # Exiting a scope (created by a flow control action)  For this we
            # point the process execution back to the entry point of the next
            # outer scope.
            if name == 'switch':
                # Tails are the ends of the switch's execution chains, we need
                # to make sure these chains don't get daisy chained.
                for tail in self.actions[self.previous_uuid]['tails']:
                    self.actions[tail]['next'] = None
            stack_id = self.pop_stack()
            self.current_uuid  = stack_id
            self.previous_uuid = stack_id
            #print 'popping stack'
                    
        elif (name == 'action'):
            self.last_action  = self.current_uuid
            self.current_uuid = self.stack_tip
            do_tails = True
                            
        self.mode = self.mode[:-1]

    def characters(self, chars):
        # Not all the chars in text may be read at once, SAX may choose to
        # chunk the data - so this operation always needs to be treated as
        # an append.
        if ((self.current_mode == BPML_EXTENSION_MODE) and (self.current_uuid is not None)):
            if (self.name is None):
                self.log.warn('Extension data with no name.')
            else:
                # TODO: Deal with chunks
                #tmp = self.actions[self.scope[-1]]['params'].get(self.name, '')
                #self.actions[self.scope[-1]]['params'][self.name] = u'{0}{1}'.format(tmp, chars)
                if ('params' not in self.actions[self.current_uuid]):
                    tmp = self.actions[self.current_uuid]['params'] = { }
                tmp = self.actions[self.current_uuid]['params'].get(self.name, '')
                self.actions[self.current_uuid]['params'][self.name] = u'{0}{1}'.format(tmp, chars)
                tmp = None

    def get_processes(self):
        return self.result
        
