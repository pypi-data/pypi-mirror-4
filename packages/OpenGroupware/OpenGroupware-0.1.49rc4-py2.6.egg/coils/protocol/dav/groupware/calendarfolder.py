#
# Copyright (c) 2009, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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


'''
    TODO: Implement WebDAV "group" property RFC3744 (Access Control) Issue#157
          Implement CALDAV:calendar-description property Issue#115
    NOTES: 2010-08-09 Implemented WebDAV "owner" property RFC2744 (Access Control)
'''

class CalendarFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self._start = None
        self._end   = None

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
                if (event.caldav_uid is None):
                    self.insert_child(event.object_id, event, alias='{0}.ics'.format(event.object_id))
                else:
                    self.insert_child(event.object_id, event, alias=event.caldav_uid)
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
        if (name == '.ctag'):
            if (self.is_collection_folder):
                return self.get_ctag_representation(self.get_ctag_for_collection())
            else:
                return self.get_ctag_representation(self.get_ctag_for_entity('Date'))
        elif ((name in ('.json', '.ls')) and (self.load_contents())):
            return self.get_collection_representation(name, self.get_children())
        else:
            entity   = None
            if (self.is_collection_folder):
                if (auto_load_enabled and self.load_contents()):
                    entity = self.get_child(name)
            else:
                if (self.load_contents()):
                    result = self.get_child(name)
                    if (result is not None):
                        return result
            (object_id, payload_format, entity, values) = self.get_appointment_for_key(name)
            if (entity is not None):
                return self.get_entity_representation(name, entity, is_webdav=is_webdav)
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
        ''' Preocess a report request '''
        payload = self.request.get_request_payload()
        self.log.debug('REPORT REQUEST: %s' % payload)
        parser = Parser.report(payload, self.context.user_agent_description)
        if (parser.report_name == 'calendar-query'):
            self._start = parser.parameters.get('start', None)
            self._end   = parser.parameters.get('end', None)
            resources = []
            if (self.load_contents()):
                for child in self.get_children():
                    if child.caldav_uid is None: name = u'{0}.ics'.format(child.object_id)
                    else: name = child.caldav_uid
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
            raise CoilsException('Unsupported report {0} in {1}'.format(parser.report_name, self))

    def apply_permissions(self, appointment):

        pass

    def do_PUT(self, name):
        ''' Process a PUT request '''
        self.log.debug('PUT request with name {0}'.format(name))
        payload = self.request.get_request_payload()
        (object_id, payload_format, appointment, payload_values) = self.get_appointment_for_key_and_content(name, payload)
        if_etag = self.request.headers.get('If-Match', None)
        if (if_etag is None):
            self.log.warn('Client issued a put operation with no If-Match!')
        else:
            # TODO: Implement If-Match test
            self.log.warn('If-Match test not implemented at {0}'.format(self.url))
        if (appointment is None):
            # Create appointment
            appointment = self.context.run_command('appointment::new', values=payload_values)
            appointment.caldav_uid = name
            self.apply_permissions(appointment)
            self.context.commit()
            self.request.simple_response(201,
                                         headers = {
                                            'Etag': '{0}:{1}'.format(appointment.object_id, appointment.version)
                                         } )
        else:
            if (isinstance(payload_values, list)):
                payload_values = payload_values[0]
            self.context.run_command('appointment::set', object=appointment,
                                                         values=payload_values)
            self.context.commit()
            self.request.simple_response(204,
                                         headers = {
                                            'Etag': '{0}:{1}'.format(appointment.object_id, appointment.version)
                                         } )

    def do_DELETE(self, name):
        ''' Process a DELETE request '''
        self.log.debug('DELETE request with name {0}'.format(name))
        (object_id, payload_format, appointment, payload_values) = self.get_appointment_for_key(name)
        if (appointment is not None):
            if(self.context.run_command('appointment::delete', object=appointment)):
                self.context.commit()
                self.request.simple_response(204)
                return
        self.no_such_path()