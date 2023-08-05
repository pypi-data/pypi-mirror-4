#
# Copyright (c) 2009, 2011, 2012
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
from StringIO                          import StringIO
from datetime                          import datetime, timedelta
from coils.foundation                  import CTag, ServerDefaultsManager
from coils.core                        import *
import  coils.core.icalendar
from coils.net                         import DAVFolder, \
                                                OmphalosCollection, \
                                                OmphalosObject, \
                                                Parser, \
                                                Multistatus_Response
from groupwarefolder                   import GroupwareFolder
from eventobject                       import EventObject
from processcalendar                   import ProcessCalendarFolder
from coils.core.icalendar              import Parser as VEvent_Parser


'''
    TODO: Implement WebDAV "group" property RFC3744 (Access Control) Issue#157
          Implement CALDAV:calendar-description property Issue#115
    NOTES: 2010-08-09 Implemented WebDAV "owner" property RFC2744 (Access Control)
'''

MIMESTRING_TO_FORMAT = { 'text/calendar': 'ics',
                         'text/json':     'json',
                         'text/yaml':     'yaml',
                         'text/xml':      'xml', }
            
def mimestring_to_format( mimestring ):
    return MIMESTRING_TO_FORMAT.get( mimestring.lower(), 'ics' ) if mimestring else 'ics'

class CalendarFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self._start = None
        self._end   = None

    @property
    def managed_entity(self):
        return 'Appointment'

    def supports_PUT(self):
        if (self.workflow_folder):
            return False
        return True

    def supports_DELETE(self):
        return True

    def supports_REPORT(self):
        return True

    def _get_overview_range(self, **params):
        events = self.context.run_command('appointment::get-overview-range', **params)
        return events

    def _get_personal_range(self, **params):
        events = self.context.run_command('appointment::get-range', **params)
        return events

    def _get_calendar_range(self, **params):
        events = self.context.run_command('appointment::get-calendar', **params)
        return events

    # PROP: OWNER

    def get_property_webdav_owner(self):
        return u'<D:href>/dav/Contacts/{0}.vcf</D:href>'.format(self.context.account_id)

    def get_property_webdav_resourcetype(self):
        return '<D:collection/><C:calendar/><G:vevent-collection/>'

    # PROP: GETCTAG

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    def get_ctag(self):
        return self.get_ctag_for_entity('Date')

    # PROP: calendar-description (RFC4791)

    def get_property_caldav_calendar_description(self):
        if (self.is_collection_folder):
            if (self.name == 'Personal'):
                return unicode('User participatory Events')
            else:
                # TODO: We assume non-Personal is Overview
                return unicode('Panel participatory events')
        else:
            return ''

    # PROP: supported-calendar-component-set (RFC4791)

    def get_property_caldav_supported_calendar_component_set(self):
        return unicode('<C:comp name="VEVENT"/>')

    @property
    def is_collection_folder(self):
        if (self.is_favorites_folder):
            return True
        if (self.parent.__class__.__name__ == 'CalendarFolder'):
            # Subfolder, contains an event collection
            return True
        return False

    def _load_contents(self):
        # TODO: Read range from server configuration
        self.log.info('Loading content in calendar folder for name {0}'.format(self.name))
        if (self.is_collection_folder):
            if (self._start is None): self._start = datetime.now() - timedelta(days=180)
            if (self._end is None): self._end   = datetime.now() + timedelta(days=120)
            if (self.name == 'Personal'):
                events = self._get_personal_range(start = self._start,
                                                  end   = self._end,
                                                  visible_only = True)
            else:
                # TODO: We assume non-Personal is Overview
                events = self._get_overview_range(start = self._start,
                                                  end   = self._end,
                                                  visible_only = True)
            # An event may have a CalDAV UID which a dumb client may reference
            for event in events:
                alias = event.href if event.href else event.uid if event.uid else '{0}.ics'.format( event.object_id )
                self.insert_child( event.object_id, event, alias=alias )
        else:
            self.insert_child('Personal', CalendarFolder(self, 'Personal', context=self.context,
                                                                           request=self.request))
            self.insert_child('Overview', CalendarFolder(self, 'Overview', context=self.context,
                                                                           request=self.request))
            self.insert_child('Processes', ProcessCalendarFolder(self, 'Processes', context=self.context,
                                                                            request=self.request))
            #ud = ServerDefaultsManager()
            #calendars = ud.default_as_list('LSCalendars')
            #for calendar in calendars:
            #    self.data[calendar] = CalendarFolder(self, calendar, context=self.context, request=self.request)
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
            format, extension, caldav_id, object_id = self.inspect_name( name, default_format = 'ics' )
            if self.is_collection_folder:
                if ( self.load_contents( ) and ( auto_load_enabled ) ):
                    event = self.get_child( name )
                    if not event:
                        event = self.get_child( caldav_id )
            else:
                self.load_contents( )
                result = self.get_child(caldav_id)
                if (result is not None):
                    return result
                event = self.context.run_command( 'appointment::get', uid=caldav_id, href=name )
                
            if event:
                return self.get_entity_representation(name, event, location=location,
                                                                   representation = format,
                                                                   is_webdav=is_webdav)
        self.no_such_path()

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
        ''' Process a report request '''
        payload = self.request.get_request_payload()
        self.log.debug('REPORT REQUEST: %s' % payload)
        parser = Parser.report(payload, self.context.user_agent_description)
        if parser.report_name == 'principal-match':
            resources = []
            if self.load_contents( ):
                for child in self.get_children():
                    if isinstance( child, Contact):
                        name = child.href if child.href else child.uid if child.uid else u'{0}.ics'.format( child.object_id )
                    elif isinstance( child, DAVFolder ):
                        name = child.name
                    resources.append(EventObject(self, name,
                                                 entity=child,
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
                                             mimetype='text/xml; charset="utf-8"')            
        elif parser.report_name == 'calendar-query':
            self._start = parser.parameters.get('start', None)
            self._end   = parser.parameters.get('end', None)
            resources = []
            if (self.load_contents()):
                for child in self.get_children():
                    if isinstance( child, Appointment):
                        name = child.href if child.href else child.uid if child.uid else u'{0}.ics'.format( child.object_id )
                    elif isinstance( child, DAVFolder ):
                        name = child.name
                    resources.append(EventObject(self, name,
                                                 entity=child,
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
                                             mimetype='text/xml; charset="utf-8"')
        elif (parser.report_name == 'calendar-multiget'):
            if (self.load_contents()):
                resources = [ ]
                for href in parser.references:
                    key = href.split('/')[-1]
                    try:
                        entity = self.get_object_for_key(key)
                        resources.append(entity)
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
                                             mimetype='text/xml; charset="utf-8"')
        else:
            raise CoilsException('Report {0} not supported on {1}'.format( parser.report_name, self ) )

    def apply_permissions(self, appointment):

        pass

    def do_PUT(self, name):
        
        if_etag = self.request.headers.get('If-Match', None)
        if (if_etag is None):
            self.log.warn('Client issued a put operation with no If-Match!')
        else:
            # TODO: Implement If-Match test
            self.log.warn('If-Match test not implemented at {0}'.format(self.url))
        
        format = mimestring_to_format( self.request.headers.get( 'Content-Type', None ) )
        format, extension, caldav_id, object_id = self.inspect_name( name, default_format = format )
        payload = self.request.get_request_payload( )
        
        if format == 'ics':
            payload = VEvent_Parser.Parse( payload, self.context )
        else:
            raise NotImplementedException( 'PUT of object format "{0}" not implemented'.format( format ) )
            
        if len( payload ) == 1:
            payload = payload[ 0 ]
            object_id = self.convert_uid_to_object_id( payload.get( 'uid', None ) )
            
            if object_id:    
                appointment = self.context.run_command( 'appointment::get', id=object_id )
            else:
                appointment = self.context.run_command( 'appointment::get', uid=caldav_id )

            if not appointment:
                #Create                
                appointment = self.context.run_command( 'appointment::new', values=payload )
                # HACK: Very sadly, most CalDAV clients are stupid and inconsistent, the UID encoded
                #       in the payload is not consistent with the HREF used to store the resource on
                #       the server.  Clients like to do silly things like add file extensions to the
                #       UID in the HREF, and then they can't find the resource they just created.  Sigh.
                appointment.href = name
                self.apply_permissions( appointment )
                self.context.commit( )
                self.request.simple_response( 201,
                                              data=None,
                                              mimetype=u'text/calendar; charset=utf-8',
                                              headers={ 'Etag':     u'{0}:{1}'.format(appointment.object_id, appointment.version) } )
            else:
                #Update
                appointment = self.context.run_command( 'appointment::set', object=appointment, values=payload )
                self.context.commit( )
                self.request.simple_response( 204,
                                              data=None,
                                              mimetype=u'text/calendar; charset=utf-8',
                                              headers={ 'Etag':     u'{0}:{1}'.format(appointment.object_id, appointment.version), } )
        else:
            raise NotImplementedException( 'Multi-PUT not implemented, and not standard.' )

    def do_DELETE(self, name):
        ''' Process a DELETE request '''
        self.log.debug( 'DELETE request with name {0}'.format( name ) )
        format, extension, caldav_id, object_id = self.inspect_name( name, default_format = 'ics' )
        appointment = self.context.run_command( 'appointment::get', uid=caldav_id )
        if appointment:
            if self.context.run_command( 'appointment::delete', object=appointment ):
                self.context.commit( )
                self.request.simple_response( 204 )
                return
        self.no_such_path( )
