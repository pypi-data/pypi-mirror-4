#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core          import *
from coils.core.logic    import ActionCommand

class GetSequenceValue(ActionCommand):
    __domain__ = "action"
    __operation__ = "get-sequence-value"
    __aliases__   = [ 'getSequenceValue', 'getSequenceValueAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        
        sequence_target = None
        if self._seq_scope == 'process':
            sequence_target = self.process
        elif self._seq_scope == 'route':
            sequence_target = self.process.route
        elif self._seq_scope == 'global':
            raise NotImplementedException()
        else:
            raise CoilsException('Invalid execution path! Possible security model violation.')
        
        if not sequence_target:
            raise CoilsException('Unable to determine the target for scope of sequence "{0}"'.format(self._seq_name))
            
        prop = self._ctx.property_manager.get_property(sequence_target, 'http://www.opengroupware.us', self._seq_name)
        
        value = None    
        if prop:
            value = prop.get_value()
            if value:
                try:
                    value = long(value)
                except:
                    error = 'Workflow sequence value is corrupted: sequence={0} value="{1}" scope={2}'.format(self._seq_name, value, self._seq_scope)
                    raise CoilsException(error)
                
        if not value:
            value = self._first_value
                    
        if value:
            value = value + self._increment
            self._ctx.property_manager.set_property(sequence_target, 'http://www.opengroupware.us', self._seq_name, value)

        self.wfile.write(unicode(value))

    def parse_action_parameters(self):
        
        self._seq_name    = self.process_label_substitutions(self.action_parameters.get('name', ''))
        if not self._seq_name:
            raise CoilsException('A sequence name must be specified for getSequenceValueAction')
        self._seq_name = 'sequence_{0}'.format(self._seq_name.lower())
            
        self._seq_scope = self.action_parameters.get('scope', 'process')
        self._seq_scope = self.process_label_substitutions(self._seq_scope)
        self._seq_scope = self._seq_scope.lower()
        if self._seq_scope not in ('process', 'global', 'route'):
            error = 'scope parameter for getSequenceValueAction must be "process", "route", or "global"; value was "{0}"'.format(self._seq_scope)
            raise CoilsException(error)
        
        self._increment   = self.process_label_substitutions(self.action_parameters.get('increment', '1'))
        try:
            self._increment   = long(self._increment)
        except:
            error = 'increment parameter for getSequenceValueAction must be numeric; value was "{0}"'.format(self._increment)
            raise CoilsException(error)
                
        self._first_value =self.action_parameters.get('initialValue', None)
        if self._first_value:
            self._first_value = self.process_label_substitutions(self._first_value)
            try:
                self._first_value = long(self._first_value)
            except:
                error = 'initialValue parameter for getSequenceValueAction must be numeric; value was "{0}"'.format(self._increment)
                raise CoilsException(error)
                

    def do_epilogue(self):
        pass
