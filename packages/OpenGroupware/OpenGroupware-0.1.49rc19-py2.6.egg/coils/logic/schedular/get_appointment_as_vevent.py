#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy             import *
from coils.core             import *
from coils.core.logic       import GetCommand
from coils.core.icalendar   import Render
from utility                import read_cached_vevent, cache_vevent
from command                import AppointmentCommand

class GetAppointmentAsVEvent(GetCommand, AppointmentCommand):
    __domain__ = "appointment"
    __operation__ = "get-as-vevent"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        if (params.has_key('object')):
            self.data = [params['object']]
        elif (params.has_key('objects')):
            self.data = params['objects']
        else:
            raise 'No appointments provided to command.'

    def run(self):
        results = [ ]
        for process in self.data:
            ics = read_cached_vevent(process.object_id, process.version)
            if (ics is None):
                ics = Render.render(process, self._ctx)
                if (ics is not None):
                    self.log.debug('Caching ProcessId#{0} VEVENT representation.'.format(process.object_id))
                    cache_vevent(process.object_id, process.version, ics)
            else:
                self.log.debug('Using cached ProcessId#{0} VEVENT representation.'.format(process.object_id))
            if (ics is not None):
                results.append(ics)
        return