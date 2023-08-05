#
# Copyright (c) 2009, 2012
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
from dateutil.tz   import gettz
from coils.core    import *
from render_object import *

def render_timezone(code, ctx):
    utctime = ctx.get_utctime()
    for tz_def in COILS_TIMEZONES:
        if (code == tz_def['code']):
            tz = gettz(tz_def['code'])
            break
        else:
            tz = gettz('UTC')
    is_dst = 0
    if (tz.dst(utctime).seconds > 0):
        is_dst = 1
    return { 'abbreviation':   tz_def['abbreviation'],
              'description':    tz_def['description'],
              'entityName':     'timeZone',
              'isCurrentlyDST': is_dst,
              'offsetFromGMT':  as_integer((86400 - tz.utcoffset(utctime).seconds) * -1),
              'serverDateTime': utctime.astimezone(tz) }

