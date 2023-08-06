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
import json
from StringIO                          import StringIO
from datetime                          import datetime, timedelta
from coils.foundation                  import CTag
from coils.core                        import Appointment
from coils.net                         import DAVFolder, \
                                                OmphalosCollection, \
                                                OmphalosObject, \
                                                StaticObject, \
                                                Parser, \
                                                Multistatus_Response, \
                                                CoilsException, \
                                                NotImplementedException
from taskobject                        import TaskObject
from rss_feed                          import TasksRSSFeed
from groupwarefolder                   import GroupwareFolder
import coils.core.omphalos as omphalos
from coils.core.icalendar import Parser as VEvent_Parser

MIMESTRING_TO_FORMAT = { 'text/calendar': 'ics',
                         'text/json': 'json',
                         'text/yaml': 'yaml',
                         'text/xml':  'xml', }
            
def mimestring_to_format( mimestring ):
    return MIMESTRING_TO_FORMAT.get( mimestring.lower(), 'ics' ) if mimestring else 'ics'


class TasksFolder(DAVFolder, GroupwareFolder):

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self._start = None
        self._end   = None

    def supports_DELETE(self):
        # TODO: Depend upon what type of folder I am or if I task deletion is enabled
        return True

    @property
    def managed_entity(self):
        return 'Task'

    def get_property_webdav_owner(self):
        return u'<D:href>/dav/Contacts/{0}.vcf</D:href>'.format(self.context.account_id)

    # PROP: resourcetype

    def get_property_webdav_resourcetype(self):
        return '<D:collection/><C:calendar/><G:vtodo-collection/>'

    # PROP: GETCTAG

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    def get_ctag(self):
        if (self.is_collection_folder):
            return self.get_ctag_for_collection()
        else:
            return self.get_ctag_for_entity('Job')

    # PROP: supported-calendar-component-set (RFC4791)

    def get_property_caldav_supported_calendar_component_set(self):
        return unicode('<C:comp name="VTODO"/>')

    def _load_contents(self):
        # TODO: Read range from server configuration
        self.log.info('Loading content in task folder for name {0}'.format(self.name))
        if (self.is_collection_folder):
            result = None
            if (self.is_project_folder):
                result = self.context.run_command('project::get-tasks', project=self.entity)
            if (self.is_favorites_folder):
                # Not supported
                raise NotImplementedException('Favoriting of tasks is not supported.')
            elif (self.name == 'Delegated'):
                result = self.context.run_command('task::get-delegated')
            elif (self.name == 'ToDo'):
                result = self.context.run_command('task::get-todo')
            elif (self.name == 'Assigned'):
                #TODO: Implement assigned tasks
                result = [ ]
            elif (self.name == 'Archived'):
                result = self.context.run_command('task::get-archived')
            if (result is None):
                return False
            else:
                self.data = { }
                if (self._start is None): self._start = datetime.now() - timedelta(days=1)
                if (self._end is None): self._end   = datetime.now() + timedelta(days=90)
                for task in result:
                    if ((self._start is not None) or (self._end is not None)):
                        #TODO: Implement date-range scoping
                        pass
                    # Depending on database vintage some entries may have varying levels of identification
                    alias = task.href if task.href else task.uid if task.uid else '{0}@{1}.ics'.format( task.object_id, self.context.cluster_id )
                    self.insert_child(task.object_id, task, alias=alias )
        else:
            self.insert_child('Delegated', TasksFolder(self, 'Delegated', context=self.context, request=self.request))
            self.insert_child('ToDo',      TasksFolder(self, 'ToDo',      context=self.context, request=self.request))
            self.insert_child('Archived',  TasksFolder(self, 'Archived',  context=self.context, request=self.request))
            self.insert_child('Assigned',  TasksFolder(self, 'Assigned',  context=self.context, request=self.request))
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name.startswith( '.' ):
            function_name = 'render_key_{0}'.format( name[ 1: ].lower().replace( '.', '_' ) )
            if hasattr( self, function_name ):
                return getattr( self, function_name )( name, is_webdav=is_webdav, auto_load_enabled=auto_load_enabled ) 
            else:
                self.no_such_path( )
        else:
            location = None
            format, extension, uid, object_id = self.inspect_name( name, default_format = 'ics' )
            if self.is_collection_folder:
                if ( self.load_contents( ) and ( auto_load_enabled ) ):
                    task = self.get_child( name )
                    if task: location = '/dav/Tasks/{0}'.format( task.get_file_name( ) )
            else:
                self.load_contents( )
                result = self.get_child( name )
                if result:
                    return result
                # TODO: should we use the object_id, or try to?
                task = self.context.run_command( 'task::get', uid=uid, href=name )
                
            if task:
                return self.get_entity_representation(name, task, location=location,
                                                                  representation = format,
                                                                  is_webdav=is_webdav)
            else:
                print( 'No such task for name "{0}"'.format( name ) )
        print name
        self.no_such_path( )

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, COPY, MOVE',
                    'PROPFIND, PROPPATCH, LOCK, UNLOCK, REPORT, ACL' ]
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=u'text/plain',
                                     headers={ 'DAV':           '1, 2, access-control, calendar-access',
                                               'Allow':         ','.join(methods),
                                               'Connection':    'close',
                                               'MS-Author-Via': 'DAV'} )

    def do_REPORT(self):
        ''' Preocess a report request '''
        payload = self.request.get_request_payload()
        self.log.debug('REPORT REQUEST: %s' % payload)
        parser = Parser.report(payload, self.context.user_agent_description)
        if (parser.report_name == 'calendar-query'):
            self._start = parser.parameters.get('start', None)
            self._end   = parser.parameters.get('end', None)
            if (self.load_contents()):
                resources = [ ]
                for child in self.get_children():
                    resources.append(TaskObject(self, child.get_file_name( ), entity=child,
                                               location='/dav/Tasks/{0}.ics'.format(child.object_id),
                                               context=self.context,
                                               request=self.request))
                stream = StringIO()
                properties, namespaces = parser.properties
                Multistatus_Response(resources=resources,
                     properties=properties,
                     namespaces=namespaces,
                     stream=stream)
                self.request.simple_response(207,
                                             data=stream.getvalue(),
                                             mimetype=u'text/xml; charset=utf-8')
        elif (parser.report_name == 'calendar-multiget'):
            resources = []
            self.log.info('Found {0} references in multiget'.format(len(parser.references)))
            for href in parser.references:
                try:
                    key = href.split('/')[-1]
                    resources.append(self.get_object_for_key(key))
                except NoSuchPathException, e:
                    self.log.debug('Missing resource {0} in collection'.format(key))
                except Exception, e:
                    self.log.exception(e)
                    raise e
            stream = StringIO()
            properties, namespaces = parser.properties
            Multistatus_Response(resources=resources,
                 properties=properties,
                 namespaces=namespaces,
                 stream=stream)
            self.request.simple_response(207,
                                         data=stream.getvalue(),
                                         mimetype=u'text/xml; charset=utf-8')
        else:
            raise CoilsException('Unsupported report {0} in {1}'.format(parser.report_name, self))

    def apply_permissions(self, task):
        pass

    def do_PUT(self, name):
        ''' Process a PUT request '''
        
        if_etag = self.request.headers.get('If-Match', None)
        if (if_etag is None):
            self.log.warn('Client issued a put operation with no If-Match!')
        else:
            # TODO: Implement If-Match test
            self.log.warn('If-Match test not implemented at {0}'.format(self.url))
            
        format = mimestring_to_format( self.request.headers.get( 'Content-Type', None ) )
        format, extension, uid, object_id = self.inspect_name( name, default_format = format)
        payload = self.request.get_request_payload( )
        if format == 'ics':
            payload = VEvent_Parser.Parse( payload, self.context )
        else:
            raise NotImplementedException( 'PUT of object format "{0}" not implemented'.format( format ) )
            
        if len( payload ) == 1:
            payload = payload[ 0 ]
            object_id = self.convert_uid_to_object_id( payload.get( 'uid', None ) )
            
            if object_id:    
                task = self.context.run_command( 'task::get', id=object_id )
            else:
                task = self.context.run_command( 'task::get', uid=uid, href=name )

            if not task:
                #Create 
                task = self.context.run_command( 'task::new', values=payload )
                # HACK: Very sadly, most CalDAV clients are stupid and inconsistent, the UID encoded
                #       in the payload is not consistent with the UID used to store the resource on
                #       the server.  Clients like to do silly things like add file extensions to the
                #       UID in the HREF, and then they can't find the resource they just created.  Sigh.
                task.href = name
                self.apply_permissions(task)
                self.context.commit()
                self.request.simple_response(201,
                                             data=None,
                                             mimetype=u'text/calendar; charset=utf-8',
                                             headers={ 'Etag':     u'{0}:{1}'.format(task.object_id, task.version),
                                                       'Location': u'/dav/Tasks/{0}.ics'.format( task.object_id ) } )
            else:
                #Update
                task = self.context.run_command('task::set', object=task, values=payload)
                if not task.href: task.href = name
                self.context.commit()
                self.request.simple_response(204,
                                             data=None,
                                             mimetype=u'text/calendar; charset=utf-8',
                                             headers={ 'Etag':     u'{0}:{1}'.format(task.object_id, task.version),
                                                       'Location': u'/dav/Tasks/{0}.ics'.format( task.object_id ) } )
        else:
            raise NotImplementedException( 'Multi-PUT not implemented, and not standard.' )

    def do_POST(self):

        def encode(o):
            if (isinstance(o, datetime)):
                return  o.strftime('%Y-%m-%dT%H:%M:%S')
            raise TypeError()

        mimetype = self.request.headers.get('Content-Type', None)
        detail_level = 65503
        if (mimetype == 'application/json'):
            payload = self.request.get_request_payload()
            # Parse payload
            values = json.loads(payload)
            # Get entityName from payload
            entity_name = values.get('entityName', None)
            if (entity_name is None):
                raise CoilsException('JSON content must specify an Omphalos entityName value')
            elif (entity_name == 'Task'):
                # Get objectId from payload
                try:
                    object_id = int(values.get('objectId', 0))
                except:
                    raise CoilsException('Payload contained invalid objectId value "{0}"'.format(values.get('objectId')))
                if (object_id == 0):
                    # Create Task
                    task = self.context.run_command('task::new', values=values)
                else:
                    # Update Task
                    task = self.context.run_command('task::get', id=object_id)
                    if (task is None):
                        raise CoilsException('No such task as objectId#{0} available'.format(object_id))
                    else:
                        self.context.run_command('task::set', values=values, object=task)
                result = task
            elif (entity_name == 'taskNotation'):
                # Perform Task Action (Comment)
                # Get objectId from payload
                # TODO: Process key-exception and non-numeric exception
                try:
                    object_id = None
                    object_id = int(values.get('taskObjectId'))
                except:
                    raise CoilsException('Payload contained invalid objectId value "{0}"'.format(values.get('objectId')))
                task = self.context.run_command('task::get', id=object_id)
                if (task is None):
                    raise CoilsException('No such task as objectId#{0} available'.format(object_id))
                else:
                    self.context.run_command('task::comment', values=values, task=task)
                result = task
            elif (entity_name == '_search'):
                if ('criteria' in values):
                    detail_level = values.get('detailLevel', 0)
                    #do_revolve   = values.get('revolve', 'NO')  -- Not supported for task searches
                    #eo_filter    = values.get('filter', None)  -- Not supported for task searches
                    size_limit   = int(values.get('limit', 150))
                    criteria     = values.get('criteria')
                    result = self.context.run_command('task::search', criteria=criteria, limit=size_limit)
            else:
                raise NotImplementedException('JSON POST of "{0}" entity not implemented'.format(entity_name))
            self.context.commit()
            representation = omphalos.Render.Result(result, detail_level, self.context)
            if (isinstance(result, list)):
                headers = { }
            else:
                headers={ 'Etag':              u'{0}:{1}'.format(task.object_id, task.version),
                                               'X-COILS-OBJECT-ID': task.object_id }
            self.request.simple_response(200,
                                 data=json.dumps(representation, default=encode),
                                 mimetype=u'application/json; charset=utf-8',
                                 headers=headers )
        else:
            raise NotImplementedException('POST of content-type "{0}" not implemented'.format(mimetype))

    def do_DELETE(self, name):

        if not self.supports_DELETE( ):
            raise NotImplementedException( 'DELETE operation not supported in this collection' )

        format, extension, uid, object_id = self.inspect_name( name, default_format = 'ics' )

        if ( self.is_favorites_folder and ( self.load_contents( ) ) ):
            task = self.get_child( name )
        else:
            task = self.context.run_command( 'task::get', uid=uid, href=name )
            if not task and object_id:
                task = self.context.run_command( 'task::get', id=object_id )
 
        if not task:
            self.no_such_path()

        try:

            if self.is_favorites_folder:
                # NOTE: Deletion of a contact from a favorite folder does *not* delete
                #       the contact it merely removes the favorite status.
                self.log.debug( 'Removing favorite status from OGo#{0} [Task] for userId#{1}'.\
                    format( task.object_id, self.context.account_id ) )
                self.context.run_command( 'task::remove-favorite', id=task.object_id )

            elif self.is_project_folder:
                # NOTE: Deletion of a task from a projects folder should *not* delete
                #       the task only unassign the task from the project.
                task.project_id = None
                
            else:
                # Delete the task
                self.context.run_command( 'task::delete', object=task )

            self.context.commit( )
        except Exception, e:
            self.log.exception( e )
            self.request.simple_response( 500, message='Deletion failed' )
        else:
            self.request.simple_response( 204 )
