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
import datetime, vobject
from StringIO       import StringIO
from time           import strftime
from davobject      import DAVObject
from bufferedwriter import BufferedWriter

class DateObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_getetag(self):
        return unicode('{0}:{1}:{2}'.format(self.prefix, self.entity.object_id, self.entity.version))

    def get_property_webdav_displayname(self):
        return self.display_name

    def get_property_webdav_getcontentlength(self):
        return unicode(len(self.get_representation()))

    def get_property_webdav_getcontenttype(self):
        return u'text/calendar'

    def get_property_webdav_getlastmodified(self):
        return self.most_recent_entry_datetime.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _load_contents(self):
        return True

    @property
    def date_value(self):
        if (hasattr(self, 'date')):
            return self.date
        return datetime.date.today()

    @property
    def comment_value(self):
        if (hasattr(self, 'comment')):
            return self.comment_value
        return ''

    def get_representation(self):
        if (hasattr(self, 'representation')):
            return self.representation
        calendar = vobject.iCalendar()
        event = calendar.add('vevent')
        event.add('uid').value                           = '{0}:{1}:{2}'.format(self.prefix, self.entity.object_id)
        event.add('description').value                    = self.comment_value
        event.add('status').value                         = 'CONFIRMED'
        event.add('summary').value                        = self.title
        event.add('dtstamp').value                        = datetime.datetime.now()
        event.add('dtstart').value                        = self.date_value
        event.add('X-MICROSOFT-CDO-INSTTYPE').value       = '0'
        event.add('x-coils-appointment-kind').value       = 'static'
        event.add('x-coils-post-duration').value          = '0'
        event.add('x-coils-prior-duration').value         = '0'
        event.add('x-coils-conflict-disable').value       = 'TRUE'
        event.add('class').value                          = 'PUBLIC'
        event.add('X-MICROSOFT-CDO-IMPORTANCE').value     = "0"
        event.add('X-MICROSOFT-CDO-BUSYSTATUS').value     = 'FREE'
        event.add('X-MICROSOFT-CDO-ALLDAYEVENT').value    = 'TRUE'
        event.add('X-MICROSOFT-CDO-INTENDEDSTATUS').value = 'FREE'
        event.add('transp').value = 'TRANSPARENT'
        #attendee = event.add('ATTENDEE')
        #attendee.cutype_param = 'RESOURCE'
        #attendee.role_param = 'REQ-PARTICIPANT'
        #attendee.partstat_param = 'NEEDS-ACTION'
        #attendee.rsvp_param = 'FALSE'
        #attendee.value= 'CN={0}:MAILTO={1}'.format(resource.name, email)
        self.representation = calendar.serialize()
        return self.representation

    def do_GET(self):
        payload = self.get_representation()
        if (payload is not None):
            self.request.simple_response(200,
                                         data=unicode(payload),
                                         mimetype=self.get_property_webdav_getcontenttype(),
                                         headers={ 'ETag': self.get_property_getetag() } )
            return
        else:
            raise NoSuchPathException('{0} not found'.format(self.name))
