#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from copy import deepcopy
import datetime, pytz, re
from dateutil.tz    import gettz


class AppointmentCommand(object):

    def normalize_timezone(self, timezone):
        if   (timezone is None):           return 'UTC'
        elif (timezone in ('EST', 'EDT')): return 'US/Eastern'
        return timezone

    def set_ics_properties(self):
        self.obj.calculate_special_values()
        pm = self._ctx.property_manager
        pm.set_property(self.obj, 'http://www.opengroupware.us/ics',
                                  'timezone',
                                  self.normalize_timezone(self.obj.timezone))
        if (self.obj.isAllDay == 'YES'):
            pm.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isAllDay', 'YES')
            pm.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isStartDST', 'NO')
            pm.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isEndDST', 'NO')
        else:
            pm.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isAllDay', 'NO')
            if (self.obj.isStartDST == 'YES'):
                pm.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isStartDST', 'YES')
            else:
                pm.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isStartDST', 'NO')
            if (self.obj.isEndDST == 'YES'):
                pm.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isEndDST', 'YES')
            else:
                pm.set_property(self.obj, 'http://www.opengroupware.us/ics', 'isEndDST', 'NO')

    def load_special_values(self, appointments):
        pm = self._ctx.property_manager
        for appointment in appointments:
            p = pm.get_property(appointment, 'http://www.opengroupware.us/ics', 'timezone')
            if (p is None):
                tz = 'UTC'
            else:
                tz = p.get_value()
            p = pm.get_property(appointment, 'http://www.opengroupware.us/ics', 'isAllDay')
            if (p is None):
                ad = 'NO'
            else:
                ad = p.get_value()
            p = pm.get_property(appointment, 'http://www.opengroupware.us/ics', 'isStartDST')
            if (p is None):
                sd = 'NO'
            else:
                sd = p.get_value()
            p = pm.get_property(appointment, 'http://www.opengroupware.us/ics', 'isEndDST')
            if (p is None):
                ed = 'NO'
            else:
                ed = p.get_value()
            appointment.set_special_values(tz, ad, sd, ed)
        return appointments
