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
from datetime           import datetime
from sqlalchemy         import *
from coils.core         import *

class GetProcessSchdule(AsyncronousCommand):
    __domain__ = "workflow"
    __operation__ = "get-schedule"
       
    def parse_success_response(self, data):
        self.set_return_value(data['schedule'])

    def parse_failure_response(self, data):
        self.set_return_value(None)

    def parse_parameters(self, **params):
        AsyncronousCommand.parse_parameters(self, **params)
        self._route_id = 0
        if ('route' in params):
            self._route_id = params.get('route').object_id
        elif ('route_id' in params):
            self._route_id = int(params.get('route_id'))

    def run(self):
        self.set_return_value(None)
        
        if self._ctx.amq_available:
            self.callout( 'coils.workflow.scheduler/list_jobs', 
                        { 'contextId': self._ctx.account_id,
                          'routeId':   self._route_id } )
            self.wait()
