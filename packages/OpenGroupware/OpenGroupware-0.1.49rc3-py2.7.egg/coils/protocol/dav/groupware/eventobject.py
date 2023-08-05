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
from xml.sax.saxutils import escape
from coils.core    import *
from coils.net     import DAVObject

class EventObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        if (self.entity is None):
            raise CoilsException()
        elif (isinstance(self.entity, Appointment)):
            if (self.entity.caldav_uid is None):
                self.location = '/dav/Calendar/{0}.ics'.format(self.entity.object_id)
            else:
                self.location = '/dav/Calendar/{0}'.format(self.entity.caldav_uid)
        elif (isinstance(self.entity, Process)):
            self.location = None

    def get_property_webdav_displayname(self):
        if (isinstance(self.entity, Appointment)):
            if (self.entity.title is None):
                return 'Appointment Id#{0}'.format(self.entity.object_id)
            else:
                return escape(self.entity.title)
        else:
            if (self.entity.route is not None):
                return escape(self.entity.route.name)
            return 'Unknwon'

    def get_property_webdav_owner(self):
        return u'<D:href>{0}</D:href>'.\
            format(self.get_appropriate_href('/dav/Contacts/{0}.vcf'.format(self.entity.owner_id)))

    def get_property_webdav_group(self):
        return None

    def get_property_caldav_calendar_data(self):
        return escape(self.get_representation())

    def get_representation(self):
        if (self._representation is None):
            self._representation = self.context.run_command('object::get-as-ics', object=self.entity)
        if self.context.user_agent_description['webdav']['escapeGETs']:
            return escape(self._representation)
        else:
            return self._representation
