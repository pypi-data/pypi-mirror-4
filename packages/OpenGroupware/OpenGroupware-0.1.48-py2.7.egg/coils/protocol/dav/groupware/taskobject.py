#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import io, time
from datetime                          import datetime
# Core
from coils.core                        import *
from coils.net                         import *
# DAV Classses
from coils.net                         import DAVObject

class TaskObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_representation(self):
        if (self._representation is None):
            self._representation = self.context.run_command('object::get-as-ics', object=self.entity)
        return self._representation

    def get_property_webdav_owner(self):
        return u'<D:href>{0}</D:href>'.\
            format(self.get_appropriate_href('/dav/Contacts/{0}.vcf'.format(self.entity.owner_id)))

    def get_property_caldav_calendar_data(self):
        return escape(self.get_representation())

    def get_property_webdav_contenttype(self):
        return 'calendar/ics'

    def get_property_caldav_calendar_data(self):
        return escape(self.get_representation())
