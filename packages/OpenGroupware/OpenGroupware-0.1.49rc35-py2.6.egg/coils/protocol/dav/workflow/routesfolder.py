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

    def supports_MKCOL(self):
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

    #
    # MKCOL
    #

    def do_MKCOL(self, name):
        '''
           TODO: Implement a good failure response

           201 (Created) - The collection or structured resource was created in
           its entirety.

           403 (Forbidden) - This indicates at least one of two conditions: 1)
           the server does not allow the creation of collections at the given
           location in its namespace, or 2) the parent collection of the
           Request-URI exists but cannot accept members.

           405 (Method Not Allowed) - MKCOL can only be executed on a
           deleted/non-existent resource.

           409 (Conflict) - A collection cannot be made at the Request-URI until
           one or more intermediate collections have been created.

           415 (Unsupported Media Type)- The server does not support the request
           type of the body.

           507 (Insufficient Storage) - The resource does not have sufficient
           space to record the state of the resource after the execution of this
           method.
        '''

        name_in_use = self.context.run_command( 'route::check-name', name = name )
        if name_in_use:
            raise CoilsException( 'Name already in use' )

        child = self.context.run_command( 'route::new', values = { 'name': name } )

        if child:
            self.context.commit()
            self.request.simple_response(201)
        else:
            self.request.simple_response(403)
    
    #
    # MOVE     
    #   

    def move_helper(self, name):
        # See Issue#158
        # TODO: Support the Overwrite header T/F
        ''' MOVE /dav/Projects/Application%20-%20BIE/Documents/87031000 HTTP/1.1
            Content-Length: 0
            Destination: http://172.16.54.1:8080/dav/Projects/Application%20-%20BIE/Documents/%5B%5DSheet1
            Overwrite: T
            translate: f
            User-Agent: Microsoft-WebDAV-MiniRedir/6.0.6001
            Host: 172.16.54.1:8080
            Connection: Keep-Alive
            Authorization: Basic YWRhbTpmcmVkMTIz

            RESPONSE
               201 (Created) - Created a new resource
               204 (No Content) - Moved to an existing resource
               403 (Forbidden) - The source and destination URIs are the same.
               409 - Conflict
               412 - Precondition failed
               423 - Locked
               502 - Bad Gateway
            '''

        source = self.object_for_key(name)

        # Get overwrite preference from request
        overwrite = self.request.headers.get('Overwrite', 'F').upper()
        if overwrite == 'T':
            overwrite = True
        else:
            overwrite = False

        # Determine destination
        destination = self.request.headers.get('Destination')
        destination = urlparse.urlparse(destination).path
        destination = urllib.unquote(destination)
        if not destination.startswith('/dav/'):
            raise CoilsException('MOVE cannot be performed across multiple DAV roots')
        destination = destination.split('/', 64)[2:] # The target path with leading /dav/ (the root) discarded
        target_name = destination[-1:][0] # The name of the object to be created
        target_path = destination[:-1] # The path chunks
        destination = None # Free the destination variable

        # Find the target object
        target = self.root
        try:
            for component in target_path:
                target = target.object_for_key(component)
        except:
            # Really?  Shouldn't we do something meaningful?
            pass
        else:
            pass

        self.log.debug('Request to move "{0}" to "{1}" as "{2}".'.format(source, target, target_name))

        return source, target, target_name, overwrite

    def do_MOVE(self, name):
        # See Issue#158
        # TODO: Support the Overwrite header T/F
        ''' MOVE /dav/Projects/Application%20-%20BIE/Documents/87031000 HTTP/1.1
            Content-Length: 0
            Destination: http://172.16.54.1:8080/dav/Projects/Application%20-%20BIE/Documents/%5B%5DSheet1
            Overwrite: T
            translate: f
            User-Agent: Microsoft-WebDAV-MiniRedir/6.0.6001
            Host: 172.16.54.1:8080
            Connection: Keep-Alive
            Authorization: Basic YWRhbTpmcmVkMTIz

            RESPONSE
               201 (Created) - Created a new resource
               204 (No Content) - Moved to an existing resource
               403 (Forbidden) - The source and destination URIs are the same.
               409 - Conflict
               412 - Precondition failed
               423 - Locked
               502 - Bad Gateway
            '''

        source, target, target_name, overwrite = self.move_helper(name)

        if target.entity and source.entity:

            # Ok, both the object to move and the target destination of the move exist!

            if isinstance(source.entity, Document):
                # We are copying a document (not a folder/collection)

                # Does the target already exists [making this and overwrite
                sink = target.get_object_for_key(target_name)
                if sink and not overwrite:
                    # The target already exists but overwrite was not specified
                    pass
                    # TODO: Implementists'
                elif sink and overwrite:
                    # The target already exists and overwrite is enabled
                    pass
                    # TODO: Implement

                target = self.context.run_command('document::move', document=source.entity,
                                                                    to_folder=target.entity,
                                                                    to_filename=target_name)

                if target:
                    self.context.commit() # COMMIT
                    if sink:
                        # Was a successful overwrite
                        # TODO: Do we need to provide the response with more information
                        self.request.simple_response(204)
                    else:
                        # Was the creation of a new resource
                        self.request.simple_response(201)
                    return

            elif isinstance(source.entity, Folder):
                # We are copying a folder/collection (not a document)
                # TODO: Acquire locks?
                # Generates a 207 response
                target = self.context.run_command('folder::move', folder=source.entity,
                                                                  to_folder=target.entity,
                                                                  to_filename=target_name)
                self.context.commit()
                self.request.simple_response(207)
                return
            else:
                raise CoilsException('Moving {0} via WebDAV is not supported'.format(source.entity))

        raise NotImplementedException()



    #
    # PUT
    #

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
