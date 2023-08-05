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
# THE SOFTWARE.
#
import yaml, json
from tempfile                          import mkstemp
from coils.core                        import *
from coils.net.foundation              import StaticObject
from coils.net                         import DAVFolder, OmphalosCollection
from signalobject                      import SignalObject
from workflow                          import WorkflowPresentation
from scheduleobject                    import ScheduleObject

class ScheduleFolder(DAVFolder, WorkflowPresentation):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self.payload = None

    def supports_PUT(self):
        return False

    def _load_contents(self):
        if isinstance(self.payload, list):
            return True
        self.payload = self.context.run_command('workflow::get-schedule', raise_error=True, timeout=60)
        if isinstance(self.payload, list):
            for entry in self.payload:
                name = '{0}.json'.format(entry['UUID'])
                self.insert_child(name, ScheduleObject(self, name, parameters=self.parameters,
                                                                   request=self.request,
                                                                   context=self.context,
                                                                   entry = entry) ) 
            return True
        return False

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if self.load_contents():
            if self.has_child(name, supports_aliases=False):
                return self.get_child(name, supports_aliases=False)
            elif name == '.json':
               return StaticObject(self, '.,json', context=self.context,
                                                   request=self.request,
                                                   payload=json.dumps(self.payload),
                                                   mimetype='application/json')
        raise self.no_such_path()

    def do_PUT(self, request_name):
        """ Allows schedule entries to be made via PUT """
        try:
            payload = self.request.get_request_payload()
            data    = json.load(payload)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Content parsing failed')
        raise NotImplementedException('Creating schedule entries via PUT is not implemented; patches welcome.')
