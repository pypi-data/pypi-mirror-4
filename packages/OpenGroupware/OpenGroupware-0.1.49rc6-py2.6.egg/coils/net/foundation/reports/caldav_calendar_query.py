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
from xml.dom    import minidom
from pytz       import timezone
from datetime   import datetime
from namespaces import XML_NAMESPACE, ALL_PROPS
from report     import Report

class caldav_calendar_query(Report):

    def __init__(self, document, user_agent_description):
        Report.__init__(self, document, user_agent_description)

    @property
    def report_name(self):
        return 'calendar-query'

    @property
    def parameters(self):
        if (self._params is None):
            _params = {}
            ranges = self._source.getElementsByTagNameNS("urn:ietf:params:xml:ns:caldav", "time-range")
            if (len(ranges) == 0):
                ranges = self._source.getElementsByTagNameNS("http://calendarserver.org/ns/", "time-range")
            if (len(ranges) > 0):
                time_range = ranges[0]
                if (u'start' in time_range.attributes.keys()):
                    value = datetime.strptime(time_range.attributes['start'].value, '%Y%m%dT%H%M%SZ')
                    value = value.replace(tzinfo=timezone('UTC'))
                    _params['start'] = value
                if (u'end' in time_range.attributes.keys()):
                    value = datetime.strptime(time_range.attributes['end'].value, '%Y%m%dT%H%M%SZ')
                    value = value.replace(tzinfo=timezone('UTC'))
                    _params['end'] = value
            self._params = _params
        return self._params

    @property
    def command(self):
        return 'appointment::get-range'
