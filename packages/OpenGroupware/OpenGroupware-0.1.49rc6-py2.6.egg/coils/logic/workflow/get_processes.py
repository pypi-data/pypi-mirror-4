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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from utility            import filename_for_process_markup

class GetProcesses(GetCommand):
    __domain__ = "route"
    __operation__ = "get-processes"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        #TODO: This should allow "route" as an alias for "object"
        if (self.query_by is None):
            if ('name' in params):
                self.query_by = 'name'
                self.name = params['name']
            elif ('object' in params):
                self.query_by = 'object_id'
                self.object_ids.append(params['object'].object_id)
            elif ('objects' in params):
                self.query_by = 'object_id'
                for route in params['objects']:
                    self.object_ids.append(route.object_id)
        # Archived
        self._archived = params.get('archived', False)
        # State
        state = params.get('state', None)
        if (state is None):
            self._state = [ 'I', 'F', 'C', 'P', 'Q', 'R' ]
        elif (isinstance(state, list)):
            # TODO: Check that "state" is a valid value?
            self._state = [str(x).upper().strip() for x in state]
        elif (isinstance(state, basestring)):
            # TODO: Check that "state" is a valid value?
            self._state = state.upper().strip()
        else:
            raise CoilsException('Unable to parse "state" parameter.')

    def set_markup(self, processes):
        for process in processes:
            handle = BLOBManager.Open(filename_for_process_markup(process), 'rb', encoding='binary')
            if (handle is not None):
                bpml = handle.read()
                process.set_markup(bpml)
                BLOBManager.Close(handle)
            else:
                self.log.error('Found no process markup for processId#{0}'.format(process.object_id))
        return processes

    def run(self):
        self.mode = 2
        route_ids = []
        if (self.query_by == 'object_id'):
            for route in self._ctx.run_command('route::get', ids=self.object_ids,
                                                              access_check=self.access_check):
                route_ids.append(route.object_id)
        elif (self.query_by == 'name'):
            route = self._ctx.run_command('route::get', name=self.name,
                                                        access_check=self.access_check)
            if (route is not None):
                route_ids.append(route.object_id)
        if (len(route_ids) > 0):
            self.log.debug('retrieving processses for routes {0}'.format(route_ids))
            db = self._ctx.db_session()
            if self._archived:
                query = db.query(Process).filter(and_(Process.route_id.in_(route_ids),
                                                      Process.state.in_(self._state),
                                                      Process.status == 'archived')).limit(self.limit)            
            else:
                query = db.query(Process).filter(and_(Process.route_id.in_(route_ids),
                                                      Process.state.in_(self._state),
                                                      Process.status != 'archived')).limit(self.limit)
            self.set_return_value(self.set_markup(query.all()))
        else:
            self.set_return_value([])
