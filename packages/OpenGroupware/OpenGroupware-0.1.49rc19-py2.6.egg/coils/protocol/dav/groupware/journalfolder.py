# Copyright (c) 2010 Tauno Williams <awilliam@whitemice.org>
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
import urllib
from StringIO                          import StringIO
from coils.core                        import NoSuchPathException
from coils.core.icalendar              import Parser as ICS_Parser
from coils.net                         import DAVFolder, \
                                                Parser, \
                                                BufferedWriter, \
                                                Multistatus_Response
from noteobject                        import NoteObject

#
# WARN: This is an implemete implementation!
#

class JournalFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    # PROP: resourcetype

    def get_property_webdav_resourcetype(self):
        return unicode('<D:collection/><C:calendar/>')

    # PROP: supported-calendar-component-set (RFC4791)

    def get_property_caldav_supported_calendar_component_set(self):
        return unicode('<C:comp name="VJOURNAL"/>')

    # OPTIONS flags

    def supports_PUT(self):
        return True

    #
    # PLUMBING
    #

    def _get_journal_project(self):
        raise NotImplementedException('')
        return None

    def _get_journal_folder(self):
        raise NotImplementedException('')
        return None

    def _load_contents(self):
        # Get journal folder
        # if journals folder does not exist then create journal folder
        project = self._get_journal_project()
        notes = self.context.run_command('folder::ls', id=folder.object_id)
        if (self.request.user_agent.supports_memos):
            # This is a VJOUNRAL aware-client, just so the content, no control objects.
            for note in notes:
                if note.kind == 'txt':
                    if (note.caldav_uid is None):
                        print 'memoId#{0} has no alias'.format(note.object_id)
                        self.insert_child(note.object_id, note, alias='{0}.vjl'.format(note.object_id))
                    else:
                        print 'memoId#{0} has alias {1}'.format(note.object_id, note.caldav_uid)
                        self.insert_child(note.object_id, note, alias=note.caldav_uid)
        else:
            # Non VJOURNAL aware-client, so show everything (assuming generic WebDAV client)
            for note in notes:
                if note.kind == 'txt':
                    self.insert_child(note.title, note)
                elif note.kind == 'ini':
                    self.insert_child(note.title, note)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if  (self.load_contents()):
            if (self.has_child(name)):
                return NoteObject(self, name, entity=self.get_child(name),
                                               request=self.request,
                                               context=self.context)
        self.no_such_path()

    #
    # REQUEST HANDLERS
    #

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

    def do_PUT(self, request_name):
        folder = self._get_journal_folder()
        mimetype = self.request.headers.get('CONTENT-TYPE', 'text/plain').split(';')[0].lower()
        # TODO: Support If-Match header!
        if (self.load_contents()):
            self.log.debug('Requested label is {0}.'.format(request_name))
            payload = self.request.get_request_payload()
            # Process payload and request name
            if (mimetype == 'text/calendar'):
                # CalDAV Mode (memo operations)
                values = ICS_Parser.Parse(payload, self.context)[0]
                if ('object_id' in values):
                    note = self.context.run_command('note::get', id=values['object_id'])
                elif (self.has_child(request_name)): note = self.get_child(request_name)
                else: note = None
            else:
                # WebDAV Mode (file operations)
                values = None
                if (self.has_child(request_name)): note = self.get_child(request_name)
                else: note = None
            # Perform operations
            if (note is None):
                print '___CREATE____'
                # create
                if (values is None):
                    # file create
                    note = self.context.run_command('note::new', values={'title': request_name },
                                                                 text=payload)
                else:
                    # vjournal create
                    note = self.context.run_command('note::new', values=values,
                                                                 context=self.entity)
                    print 'setting caldav_uid = {0}'.format(request_name)
                    note.caldav_uid = request_name
                # TODO: Add to journal folder
                self.request.simple_response(201,
                                             data=None,
                                             mimetype=u'{0}; charset=utf-8'.format(mimetype),
                                             headers={ 'Etag':     u'{0}:{1}'.format(note.object_id, note.version) } )
            else:
                print '___UPDATE____'
                # update
                if (values is None):
                    # file update
                    note = self.context.run_command('note::set', object=note,
                                                                 context=self.entity,
                                                                 text=payload)
                else:
                    # vjournal update
                    note = self.context.run_command('note::set', object=note,
                                                                 context=self.entity,
                                                                 values=values)
            self.context.commit()
            self.request.simple_response(204,
                                         data=None,
                                         mimetype=u'{0}; charset=utf-8'.format(mimetype),
                                         headers={ 'Etag':     u'{0}:{1}'.format(note.object_id, note.version) } )

    def do_REPORT(self):
        folder = self._get_journal_folder()
        ''' Preocess a report request '''
        payload = self.request.get_request_payload()
        self.log.debug('REPORT REQUEST: %s' % payload)
        parser = Parser.report(payload)
        if (parser.report_name == 'calendar-query'):
            self._start = parser.parameters.get('start', None)
            self._end   = parser.parameters.get('end', None)
            if (self.load_contents()):
                # TODO: Do VJOURNAL objects need CalDAV UID support
                resources = [ ]
                for note in self.get_children():
                    if (note.caldav_uid is None):
                        name = u'{0}.vjl'.format(note.object_id)
                    else:
                        name = note.caldav_uid
                    resources.append(NoteObject(self, name, entity=note,
                                                request=self.request,
                                                context=self.context))
                stream = StringIO()
                properties, namespaces = parser.properties
                Multistatus_Response(resources=resources,
                                     properties=properties,
                                     namespaces=namespaces,
                                     stream=stream)
                self.request.simple_response(207,
                                             data=stream.getvalue(),
                                             mimetype='text/xml; charset="utf-8"',
                                             headers={  } )
        elif (parser.report_name == 'calendar-multiget'):
            resources = [ ]
            self._start = parser.parameters.get('start', None)
            self._end   = parser.parameters.get('end', None)
            for href in parser.references:
                key = href.split('/')[-1]
                try:
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
                                         mimetype='text/xml; charset="utf-8"',
                                         headers={  } )
        else:
            raise CoilsException('Unsupported report {0} in {1}'.format(parser.report_name, self))

    def do_DELETE(self, name):
        folder = self._get_journal_folder()
        if (self.load_contents()):
            if (self.has_child(name)):
                # TODO: Catch exceptions and return an appropriate error
                self.context.run_command('contact::delete', object=self.get_child(name))
                self.context.commit()
                self.request.simple_response(204,
                             data=None,
                             mimetype=self.entity.get_mimetype(),
                             headers={ } )
            else:
                self.no_such_path()
        else:
            raise CoilsException('Unable to enumerate collection contents.')
