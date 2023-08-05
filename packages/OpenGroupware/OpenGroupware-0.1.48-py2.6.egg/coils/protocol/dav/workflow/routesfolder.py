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
# THE SOFTWARE.
#
import os
from tempfile                          import mkstemp
from coils.core                        import *
from coils.net                         import DAVFolder, OmphalosCollection
from routefolder                       import RouteFolder
from utility                           import compile_bpml
from signalobject                      import SignalObject
from workflow                          import WorkflowPresentation

class RoutesFolder(DAVFolder, WorkflowPresentation):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def supports_PUT(self):
        return True

    def _load_contents(self):
        self.data = { }
        if (self.name == 'Routes'):
            # Implemented
            self.log.debug('Returning enumeration of available routes.')
            routes = self.context.run_command('route::get', properties=[ Route ])
            for route in routes:
                self.insert_child(route.name, route)
        else:
            return False
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        #
        # Support retriving a specific key without loading all the routes
        #
        if (name == 'signal'):
            return SignalObject(self, name,
                                 parameters=self.parameters,
                                 entity=None,
                                 context=self.context,
                                 request=self.request)
        elif (name in ('.ls', '.json', '.contents')):
            # REST Request
            if (self.load_contents()):
                if (name in ('.json', '.contents')):
                    return OmphalosCollection(self, name,
                                               detailLevel=65535,
                                               rendered=True,
                                               data=self.get_children(),
                                               parameters=self.parameters,
                                               context=self.context,
                                               request=self.request)
                elif (name == '.ls'):
                    return OmphalosCollection(self, name,
                                               rendered=False,
                                               data=self.get_children(),
                                               parameters=self.parameters,
                                               context=self.context,
                                               request=self.request)
        else:
			# We assume the name requested relates to the name of a route
            if self.is_loaded:
                route = self.get_child(name)
            else:
                route = self.context.run_command('route::get', name=name)
            if route:
                return RouteFolder(self,
                                    name,
                                    parameters=self.parameters,
                                    entity=route,
                                    context=self.context,
                                    request=self.request)
        raise self.no_such_path()

    def do_PUT(self, request_name):
        """ Allows routes to be created by dropping BPML documents into /dav/Routes """
        bpml = BLOBManager.ScratchFile(suffix='bpml')
        bpml.write(self.request.get_request_payload())
        description, cpm = compile_bpml(bpml, log=self.log)
        try:
            route = self.context.run_command('route::new', values=description, handle=bpml)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Route creation failed.')
        BLOBManager.Close(bpml)
        self.context.commit()
        self.request.simple_response(301,
                                     headers = { 'Location': '/dav/Workflow/Routes/{0}/markup.xml'.format(route.name),
                                                 'Content-Type': 'text/xml' } )
