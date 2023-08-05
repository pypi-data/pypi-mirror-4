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


'''
    TODO: Implement WebDAV "group" property RFC2744 (Access Control)
    NOTES: 2010-08-09 Implemented WebDAV "owner" property RFC2744 (Access Control)
'''

class ProcessCalendarFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self._start = None
        self._end   = None

    def supports_PUT(self):
        return False

    def supports_DELETE(self):
        return True

    def supports_REPORT(self):
        return True

    def _get_process_range(self, **params):
        events = self.context.run_command('process::get-range', **params)
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
        return self.get_ctag_for_entity('Process')

    # PROP: calendar-description (RFC4791)

    def get_property_caldav_calendar_description(self):
        # TODO: Implement
        return ''

    # PROP: supported-calendar-component-set (RFC4791)

    def get_property_caldav_supported_calendar_component_set(self):
        return unicode('<C:comp name="VEVENT"/>')

    @property
    def is_collection_folder(self):
        return False

    def _load_contents(self):
        # TODO: Read range from server configuration
        self.log.info('Loading content in calendar folder for name {0}'.format(self.name))
        if (self._start is None): self._start = datetime.now() - timedelta(days=90)
        if (self._end is None): self._end   = datetime.now() + timedelta(days=30)
        events = self._get_process_range(start = self._start,
                                         end   = self._end,
                                         visible_only = True)
        for event in events:
            self.insert_child(event.object_id, event, alias='{0}.ics'.format(event.object_id))
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == '.ctag'):
            return self.get_ctag_representation(self.get_ctag_for_entity('Process'))
        else:
            (object_id, payload_format, entity, values) = self.get_process_for_key(name)
            if (entity is not None):
                return EventObject(self, name, entity=entity,
                                                context=self.context,
                                                request=self.request)
        self.log.debug('No such path for key {0}'.format(name))
        self.no_such_path()

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'OPTIONS, GET, HEAD, DELETE, TRACE',
                    'PROPFIND, PROPPATCH, REPORT, ACL' ]
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
                    name = u'{0}.ics'.format(child.object_id)
                    resources.append(EventObject(self, name, entity=child,
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
            resources = [ ]
            self.log.debug('calendar-multiget')
            for href in parser.references:
                self.log.debug('href: {0}'.format(href))
                key = href.split('/')[-1]
                try:
                    entity = self.get_object_for_key(key)
                    self.log.debug(entity)
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
