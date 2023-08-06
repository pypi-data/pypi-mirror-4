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
import urlparse, urllib
from coils.core          import Folder
from uuid                import uuid4
from documentsfolder     import DocumentsFolder

class CabinetsFolder(DocumentsFolder):
    def __init__(self, parent, name, **params):
        DocumentsFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        contents = self.context.run_command('account::get-cabinets')
        for entity in contents:
            self.insert_child(entity.name, entity)
        return True

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
        
        project_name = uuid4().hex
        
        project = self.context.run_command('project::new', values = { 'name':    project_name,
                                                                      'number':  project_name,
                                                                      'is_fake': 1,
                                                                      'kind':    'opengroupware.coils.cabinet' } )
        self.context.run_command('project::set-contacts', project=project, contact_ids = [ self.context.account_id ] )
        self.context.run_command('object::set-acl', object=project, 
                                                    context_id=self.context.account_id,
                                                    permissions='rwasdlc') 
        folder = self.context.run_command('project::get-root-folder', project=project)
        folder.name = name
        self._update_properties(folder)
        self.context.commit()
        self.request.simple_response(201)

    #
    # DELETE
    #

    def do_DELETE(self, name):
        # TODO: Implement me!
        if (self.load_contents()):
            if (self.has_child(name)):
                child = self.get_child(name)
                self.log.debug('Request to delete {0}'.format(child))
                if isinstance(child, Folder):
                    self.log.debug('Request to delete folder "{0}"'.format(name))
                    project = self.context.run_command('project::get', id=child.project_id)
                    self.context.run_command('project::delete', object=project)
                    self.context.commit()
        self.request.simple_response(204)

    #
    # MOVE
    #

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
        destination = destination.split('/', 64)[2:] # The target path with leading /dav/ (the root) discarded
        target_name = destination[-1:][0] # The name of the object to be created
        target_path = destination[:-1] # The path chunks
        
        if len(target_path) != 1 or target_path[0] != 'Cabinets':
            self.request.simple_response(403, data='Cabinet folders cannot be moved from the Cabinets folder')
            return
        destination = None # Free the destination variable

        # Find the target object
        target = self.root
        try:
            for component in target_path:
                target = target.object_for_key(component)
        except:
            pass
        else:
            pass
        self.log.debug('Request to move "{0}" to "{1}" as "{2}".'.format(source, target, target_name))

        if source.entity:
            if isinstance(source.entity, Folder):
                # We are copying a folder/collection (not a document)
                # TODO: Acquire locks?
                # Generates a 207 response
                target = self.context.run_command('folder::move', folder=source.entity,
                                                                  to_folder=None,
                                                                  to_filename=target_name)
                self._update_properties(target)
                self.context.commit()
                self.request.simple_response(207)
                return
            else:
                raise CoilsException('Moving {0} via Cabinets [WebDAV] is not supported'.format(source.entity))

        raise NotImplementedException()

    def _update_properties(self, folder):
        cabinet_name = folder.name.lower().replace(' ', '_').replace('-', '_')
        self.context.property_manager.set_property(folder, 'http://www.opengroupware.us/cabinets', 'name', cabinet_name)
        project = self.context.run_command('project::get', id=folder.project_id)
        if project:
            self.context.property_manager.set_property(project, 'http://www.opengroupware.us/cabinets', 'name', cabinet_name)
