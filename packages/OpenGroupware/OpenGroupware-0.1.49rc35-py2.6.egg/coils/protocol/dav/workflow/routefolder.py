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
# THE SOFTWARE.
#
from coils.core                        import *
from coils.net                         import *
from processfolder                     import ProcessFolder
from bpmlobject                        import BPMLObject
from versionsfolder                    import VersionsFolder
from signalobject                      import SignalObject
from proplistobject                    import PropertyListObject
from workflow                          import WorkflowPresentation

class RouteFolder(DAVFolder, WorkflowPresentation):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self.entity = params['entity']
        self.route_id = self.entity.object_id
        self.archived = bool(params.get('archived', False))

    def supports_PUT(self):
        return True

    def _load_contents(self):
        self.data = { }
        self.log.debug('Returning enumeration of processes of route {0}.'.format(self.name))
        processes = self.context.run_command('route::get-processes', id=self.route_id, archived=self.archived)
        for process in processes:
            self.insert_child(str(process.object_id), process)
        if not self.archived:
            self.insert_child('markup.xml', None)
            self.insert_child('Versions', None)
            self.insert_child('propertyList.txt', None)
            self.insert_child('Archive', None)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        # TODO: This is long and clunky, find a better way to map name to responses
        self.log.debug('Request for folder key {0}'.format(name))
        if (name == 'signal'):
            return SignalObject(self, name,
                                 parameters=self.parameters,
                                 entity=self.entity,
                                 context=self.context,
                                 request=self.request)
        elif (name == 'markup.xml'):
            return BPMLObject(self, name,
                               parameters=self.parameters,
                               entity=self.entity,
                               context=self.context,
                               request=self.request)
        elif (name == 'Versions'):
            return VersionsFolder(self, name,
                                   parameters=self.parameters,
                                   entity=self.entity,
                                   context=self.context,
                                   request=self.request)
        elif (name == 'Archive'):
            return RouteFolder(self, name,
                               parameters=self.parameters,
                               entity=self.entity,
                               context=self.context,
                               archived=True,
                               request=self.request)
        elif (name == 'propertyList.txt'):
            return PropertyListObject(self, name,
                                       parameters=self.parameters,
                                       entity=self.entity,
                                       context=self.context,
                                       request=self.request)
        elif (name in ('.json', '.contents', '.ls')):
            result = [ ]
            for process in self.context.run_command('route::get-processes', id=self.route_id):
                if process.owner_id in self.context.context_ids:
                    result.append(process)
            if (name == '.ls'):
                rendered = False
            else:
                rendered = True
            return OmphalosCollection(self, name,
                                       detailLevel=65535,
                                       rendered=rendered,
                                       data=result,
                                       parameters=self.parameters,
                                       context=self.context,
                                       request=self.request)
        else:
            if (self.is_loaded):
                # Contents of folder is already loaded, so just check for the process
                if (self.has_child(name)):
                    process = self.get_child(name)
                else:
                    process = None
            else:
                # Convert the requested name to a Process Id (Process objectId) so we can attempt to retrieve it
                try:
                    pid = int(name)
                except:
                    # Issue#151: Non-numeric unknown key requires to RouteFolder results in a 500 response
                    # If the requested key is not an integer than it cannot be a process id and we want
                    # to fail with a nice no-such-path response
                    self.no_such_path()
                # Get the requested process from Logic/ORM
                process = self.context.run_command('process::get', id=pid)
            if (process is not None):
                return ProcessFolder(self, name,
                                      parameters=self.parameters,
                                      entity=process,
                                      context=self.context,
                                      request=self.request)
        self.no_such_path()

    def do_PUT(self, request_name):
        if self.archived:
            raise CoilsException('PUT not supported in archived context')
        payload = self.request.get_request_payload()
        if (request_name in ['markup.xml', 'markup.bpml']):
            self.context.run_command('route::set', object=self.entity, markup=payload)
            self.context.commit()
            self.request.simple_response(201)
        else:
            self.log.debug('Attempting to create new process from route {0}'.format(self.route_id))
            try:
                mimetype = self.request.headers.get('Content-Type', 'application/octet-stream')
                process = self.create_process(route=self.entity,
                                              data=payload,
                                              priority=201,
                                              mimetype=mimetype)
                if (len(self.parameters) > 0):
                    for key, value in self.parameters.items():
                        key = 'xattr_{0}'.format(key.lower().replace(' ', ''))
                        if value is None:
                            value = 'YES'
                        elif (len(value) > 0):
                            value = str(value[0])
                        self.context.property_manager.set_property(process,
                                                                   'http://www.opengroupware.us/oie',
                                                                   key, value)
                self.context.commit()
                self.log.info('Process {0} created via DAV PUT by {1}.'\
                    .format(process.object_id, self.context.get_login()))
                message = self.get_input_message( process )
                self.start_process( process )
            except Exception, e:
                self.log.exception(e)
                raise CoilsException('Failed to create process')
            paths = self.get_process_urls(process)
            self.request.simple_response(301,
                                         mimetype = message.mimetype,
                                         headers  = {
                                            'Location':                       paths['self'],
                                            'X-COILS-WORKFLOW-MESSAGE-UUID':  message.uuid,
                                            'X-COILS-WORKFLOW-MESSAGE-LABEL': message.label,
                                            'X-COILS-WORKFLOW-PROCESS-ID':    process.object_id,
                                            'X-COILS-WORKFLOW-OUTPUT-URL':    paths['output']
                                         } )

    def do_DELETE(self):
        # Terminate a process, or delete a completed process
        try:
            self.context.run_command('route::delete', object=self.entity)
            self.commit()
        except:
            self.request.simple_response(500, message='Deletion failed')
        else:
            self.request.simple_response(204, message='No Content')
