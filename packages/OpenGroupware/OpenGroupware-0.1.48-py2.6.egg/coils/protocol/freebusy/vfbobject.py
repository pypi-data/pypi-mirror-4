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
import json, vobject
from datetime   import datetime, timedelta
from coils.core import *
from coils.net  import *

class VFBObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def determine_target(self):
        # TODO: Allow the target to be specified by object id
        name = self.name
        if len(name) > 5:
            if name[-4:].lower() == '.vfb':
                result = self.context.run_command('account::get', login=name[:-4])
                if result:
                    self.requested_address = None
                    return result
        if self.parameters:
            left = self.parameters.get('name', None)
            # TODO: support just specifing e-mail directly in the URL as a parameter
            # TODO: Use the default e-mail domain for the server if none was specified
            right = self.parameters.get('server', ['morrison-ind.com'])
            right = right[0]
            if left:
                left = left[0]
                self.requested_address = '{0}@{1}'.format(left, right)
                result = self.context.run_command('contact::get', email=self.requested_address)
                if result:
                    return result[0]
        return None
        
    def determine_range(self):
        
        # TODO: Get the default range from the server's defaults
        
        if 'start' in self.parameters:
            start = datetime.strptime(self.parameters['start'][0], '%Y-%m-%d')
        else:
            start = datetime.now() - timedelta(days=30)
            
        if 'end' in self.parameters:
            end = datetime.strptime(self.parameters['end'][0], '%Y-%m-%d')
        else:
            end = start + timedelta(days=90)
            
        return start, end
        
    def determine_format(self):
        format = self.parameters.get('format', ['vfb'])
        if format:
            format = format[0]
        if format not in ('json', 'vfb'):
            return 'vfb'
        return format
            
    def render_vfb(self, target, start, end, info):
        if self.requested_address:
            # Lookup was via e-mail address, return what the client asked for
            email = self.requested_address
        else:
            # Lookup wasn't by e-mail so the use objects primary e-mail address
            email = target.get_company_value_text('email1')
        
        calendar = vobject.iCalendar()
        vfb = calendar.add('vfreebusy')
        tmp =  vfb.add('ATTENDEE')
        tmp.value = 'MAILTO:{0}'.format(email)
        tmp =  vfb.add('ORGANIZER')
        tmp.value = 'MAILTO:{0}'.format(email)
        vfb.add('dtstamp').value = datetime.now()
        vfb.add('dtstart').value = start
        vfb.add('dtend').value   = end
        for record in info:
            tmp = vfb.add('FREEBUSY')
            tmp.value = [(record['start'], record['end'])]
            if record['busy']:
                tmp.fbtype_param = 'BUSY'
            else:
                tmp.fbtype_param = 'FREE'
        return calendar.serialize()
        
    def render_json(self, target, start, end, info):
        
        def encode(o):
           if (isinstance(o, datetime)):
               return  o.strftime('%Y-%m-%dT%H:%M:%S')
           raise TypeError()
           
        return json.dumps(info, default=encode)

    def do_GET(self):
        
        # TODO: check for the desired format, defaulting to VCALENDAR.VFREEBUSY
        
        target = self.determine_target()
        
        if target:
            start, end = self.determine_range()
        else:
            raise NoSuchPathException('No Free/Busty information available for this target.')
            
        fbinfo = self.context.run_command('schedular::get-free-busy', object=target, 
                                                                      start=start, 
                                                                      end=end)
             
        format = self.determine_format()
        if format == 'vfb':
            self.request.simple_response(200, data=self.render_vfb(target=target, start=start, end=end, info=fbinfo))
        elif format == 'json':
            self.request.simple_response(200, data=self.render_json(target=target, start=start, end=end, info=fbinfo))

    def do_POST(self):
        raise CoilsException('POST operations not support for Free/Busy')
