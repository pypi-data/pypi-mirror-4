#
# Copyright (c) 2010, 2012
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
from pytz                import timezone
from datetime            import datetime, timedelta
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render

class CreateTaskAction(ActionCommand):
    __domain__    = "action"
    __operation__ = "create-task"
    __aliases__   = [ 'createTask', "createTaskAction" ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        #TODO: Support using input message as comment text (Issue#55)
        task = self._ctx.run_command( 'task::new', values=self._values )
        if task is None:
            raise CoilsException( 'Failed to create entity.' )
        if self._tiein:
            self.process.task_id = task.object_id
        results = XML_Render.render( task, self._ctx )
        self.wfile.write( results ) 
        self.wfile.flush( )

    def _get_attribute_from_params(self, name, default=None):
        x = unicode( self.action_parameters.get(name, default ) )
        return unicode( self.process_label_substitutions( x ) )

    def parse_action_parameters(self):
        self._values = {
            'comment':     self._get_attribute_from_params('comment', ''),
            'name':        self._get_attribute_from_params('name', ''),
            'start':       self._get_attribute_from_params('start', ''),
            'kind':        self._get_attribute_from_params('kind'),
            'sensitivity': self._get_attribute_from_params('sensitivity', '0'),
            'priority':    self._get_attribute_from_params('priority', '3'),
            'executorid':  self._get_attribute_from_params('executor', self._ctx.account_id),
            'ownerid':     self._get_attribute_from_params('owner', self._ctx.account_id),
            }
        # Start & End
        if ('start' not in self.action_parameters):
            self._values['start'] = datetime.now()
        else:
            self._values['start'] = datetime(int(self._values['start'][0:4]),
                                             int(self._values['start'][5:7]),
                                             int(self._values['start'][8:10]),
                                             tzinfo=timezone('UTC'))
        if ('duration' in self.action_parameters):
            self._values['end'] += self._values['start'] + timedelta(days=int(self.action_parameters.get('duration')))
        elif ('end' in self.action_parameters):
            self._values['end'] = self.process_label_substitutions(self.action_parameters.get('end'))
            
        # Project
        if 'project' in self.action_parameters:
            project_id = self._get_attribute_from_params( 'project', default=0 )
            try:
                project_id = int( project_id )
            except:
                project_id = None
            else:
                if project_id < 10003:
                    project_id = None
            self._values['project_id'] = project_id
            
        # Parent
        if 'parent' in self.action_parameters:
            parent_id = self._get_attribute_from_params( 'parent', default=0 )
            try:
                parent_id = int( parent_id )
            except:
                parent_id = None
            else:
                if parent_id < 10003:
                    parent_id = None
            self._values['parent_id'] = parent_id
                    
        if (self.action_parameters.get('workflowTask', 'YES').upper() == 'YES'):
            self._tiein = True
        else:
            self._tiein = False
