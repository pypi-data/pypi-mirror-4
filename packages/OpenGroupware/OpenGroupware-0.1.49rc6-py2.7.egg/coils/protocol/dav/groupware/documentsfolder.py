# Copyright (c) 2010, 2012 
# Adam Tauno Williams <awilliam@whitemice.org>
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
import urllib, shutil, json
from datetime                          import datetime
from shutil                            import copyfile
from coils.core                        import BLOBManager, \
                                              ServerDefaultsManager, \
                                              Document, \
                                              Folder, \
                                              CoilsException, \
                                              NotImplementedException
from coils.net                         import DAVFolder, \
                                              StaticObject, \
                                              OmphalosCollection
from documentobject                    import DocumentObject
from coils.core.omphalos               import Render as Omphalos_Render
from groupwarefolder                   import GroupwareFolder

class DocumentsFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def __repr__(self):
        return '<DocumentsFolder path="{0}" contextId="{1}" login="{2}"/>'.\
               format(self.get_path(), self.context.account_id, self.context.login)

    def _load_contents(self):
        contents = self.context.run_command('folder::ls', id=self.entity.object_id)
        for entity in contents:
            if (entity.__entityName__ == 'Folder'):
                self.insert_child(entity.name, entity)
            elif (entity.__entityName__ == 'Document'):
                if (entity.extension is not None):
                    self.insert_child('{0}.{1}'.format(entity.name, entity.extension), entity)
                else:
                    self.insert_child('{0}'.format(entity.name), entity)
        return True

    def _enumerate_folder(self, folder, depth, detail, format):
        depth -= 1
        if format == 'simple':
            y = [ ]
            ls = self.context.run_command('folder::ls', folder=folder)
            for e in ls:
                x = Omphalos_Render.Result(e, detail, self.context)
                if (e.__entityName__ == 'Folder'):
                    if (depth > 0):
                        x['children'] = self._enumerate_folder(e, depth, detail, format)
                        x['atLimit'] = False
                    else:
                        x['atLimit'] = True
                y.append(x)
        else:
            # Default structure for response is "stack"
            y = ('Folder', Omphalos_Render.Result(folder, detail, self.context), [ ])
            ls = self.context.run_command('folder::ls', folder=folder)
            for e in ls:
                if (e.__entityName__ == 'Folder'):
                    if (depth > 0):
                        y[2].extend(self._enumerate_folder(e, depth, detail, format))
                    else:
                        y[2].append(('Folder', Omphalos_Render.Result(e, detail, self.context), 'LIMIT'))
                else:
                    y[2].append(('Document', Omphalos_Render.Result(e, detail, self.context)))
        return y


    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):

        def encode(o):
            if (isinstance(o, datetime)):
                return  o.strftime('%Y-%m-%dT%H:%M:%S')
            raise TypeError()

        if (name == '.lsR'):
            depth = int(self.parameters.get('depth', [1])[0])
            detail = int(self.parameters.get('detail', [0])[0])
            format = self.parameters.get('format', ['stack'])[0]
            payload = self._enumerate_folder(self.entity, depth, detail, format)
            payload = json.dumps(payload, default=encode)
            return StaticObject(self, '.ls', context=self.context,
                                             request=self.request,
                                             payload=payload,
                                             mimetype='application/json')
        if  (self.load_contents()):
            if name in ('.ls', '.json'):
                # Get an index of the folder as an Omphalos collection
                return OmphalosCollection(self,
                                          name,
                                          data=self.get_children(),
                                          context=self.context,
                                          request=self.request)
            if self.has_child(name):
                entity = self.get_child(name)
                if (entity.__entityName__ == 'Document'):
                    return DocumentObject(self, name, entity=entity,
                                                       parameters=self.parameters,
                                                       request=self.request,
                                                       context=self.context)
                elif (entity.__entityName__ == 'Folder'):
                    return DocumentsFolder(self, name, entity=entity,
                                                        parameters=self.parameters,
                                                        request=self.request,
                                                        context=self.context)
            elif self.request.command in ('PROPPATCH', 'LOCK'):
                # A PROPPATCH or LOCK to a non-existent object CREATES A NEW EMPTY DOCUMENT!
                # This is a Microsoft thing, so don't ask.
                document = self.context.run_command('document::new', name=name,
                                                                     values = { },
                                                                     folder=self.entity)
                self.log.debug('Created document {0} in response to {1} command'.\
                    format(document, self.request.command))
                self.context.property_manager.set_property(document,
                                                           'http://www.opengroupware.us/mswebdav',
                                                           'isTransient',
                                                           'YES')
                return DocumentObject(self, name, entity=document,
                                                  parameters=self.parameters,
                                                  request=self.request,
                                                  context=self.context)
        else:
            self.no_such_path()

    def do_PUT(self, name):
        ''' Process a PUT request '''
        # TODO: Complete implementation!
        # TODO: Support If-Match header!
        # TODO: Check for locks!
        self.log.debug('Request to create {0} in folder {1}'.format(name, self.name))
        payload = self.request.get_request_payload()
        mimetype = self.request.headers.get('Content-Type', 'application/octet-stream')
        scratch_file = BLOBManager.ScratchFile()
        scratch_file.write(payload)
        scratch_file.seek(0)
        response_code = 201
        document = None
        if (self.load_contents()):
            if (self.has_child(name)):
                # Update document content
                entity = self.get_child(name)
                document = self.context.run_command('document::set', object=entity,
                                                                    values = { },
                                                                    handle=scratch_file)
                self.log.debug('Updated document {0}'.format(document))
                response_code = 204
            else:
                # Create new document
                document = self.context.run_command('document::new', name=name,
                                                                     handle=scratch_file,
                                                                     values = { },
                                                                     folder=self.entity)
                self.log.debug('Created new document {0}'.format(document))
            # A PUT operation makes a document non-transient (if it was a lock-null resource
            # it now represents a real document
            self.context.property_manager.set_property(document,
                                                       'http://www.opengroupware.us/mswebdav',
                                                       'isTransient',
                                                       'NO')
            self.context.property_manager.set_property(document,
                                                       'http://www.opengroupware.us/mswebdav',
                                                       'contentType',
                                                       mimetype)
            self.context.commit()
            
            if document:
                # Document has been realized
                if mimetype == 'application/octet-stream':
                    # Client did not provide us with a real MIME type for the content
                    # so we are going to at least supply them with our extension based
                    # best-guess regarding the type of data
                    sd = ServerDefaultsManager()
                    mime_type_map = sd.default_as_dict('CoilsExtensionMIMEMap')
                    mimetype = document.get_mimetype(type_map=mime_type_map)
                    
            #headers = { 'Content-Type': mimetype }
            # TODO: Do some user agents want Content-Length in their response?
            # 'Content-Length': str(document.file_size),
            
            headers = { }
            self.request.simple_response(response_code,
                                         mimetype = mimetype,
                                         headers  = headers  )
        else:
            # TODO; Can this happen without an exception having occurred?
            raise CoilsExcpetion('Ooops!')

    def do_DELETE(self, name):
        """
        Process the DELETE request to delete the specified name from
        the current collection.
        
        :param name: The name of the object in this colleciton to be deleted.
        """
        if (self.load_contents()):
            if (self.has_child(name)):
                child = self.get_child(name)
                self.log.debug('Request to delete {0}'.format(child))
                if (isinstance(child, Folder)):
                    self.log.debug('Request to delete folder "{0}"'.format(name))
                    self.context.run_command('folder::delete', object=child)
                    self.context.commit()
                elif (isinstance(child, Document)):
                    self.log.debug('Request to delete document "{0}"'.format(name))
                    self.context.run_command('document::delete', object=child)
                    self.context.commit()
        self.request.simple_response(204)

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
           
        child = self.context.run_command('folder::new', values = { 'name': name }, 
                                                        folder=self.entity)
        if child:
            self.context.commit()
            self.request.simple_response(201)
        else:
            self.request.simple_response(403)
        
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

