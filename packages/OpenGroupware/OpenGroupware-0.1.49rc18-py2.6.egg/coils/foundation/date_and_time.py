#!/usr/bin/env python
# Copyright (c) 2012 
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
import pytz
from datetime import datetime, date
from exceptions import DateTimeFormatException

def Parse_Value_To_UTCDateTime( time_value, date_only = False, default=None ):
    """
    Take the input value and produce a data time localized to UTC.
    
    :param time_value: The input value to be parsed
    :param date_only: By default a datetime is produced, this indicates a date is desired
    :param default: If the input value is None result this value as the result
    """
    
    utc = pytz.timezone('UTC')
    
    if not time_value:
        time_value = default
        if time_value is None:
            return time_value
        
    if isinstance( time_value, basestring ):
        time_value = time_value.strip( )
        if 'T' in time_value:
            if len( time_value ) == 15:
                time_value = datetime.strptime( time_value, '%Y%m%dT%H%M%S' )
            elif len( time_value ) == 13:
                time_value = datetime.strptime( time_value, '%Y%m%dT%H%M' )
            elif len( time_value ) == 16:                
                time_value = datetime.strptime( time_value, '%Y-%m-%dT%H:%M' )                
            elif len( time_value ) == 19:                
                time_value = datetime.strptime( time_value, '%Y-%m-%dT%H:%M:%S' )
            else:
                raise DateTimeFormatException( 'Failed to parse date string of "{0}"'.format( time_value ) )
        elif '-' in time_value:
            if len( time_value ) == 19:
                time_value = datetime.strptime( time_value, '%Y-%m-%d %H:%M:%S' )
            elif len( time_value ) == 16:
                time_value = datetime.strptime( time_value, '%Y-%m-%d %H:%M' )
            else:
                raise DateTimeFormatException( 'Failed to parse date string of "{0}"'.format( time_value ) )
        elif time_value.isnumeric:
            time_value = int( value )
        else:
            raise DateTimeFormatException( 'Fail to parse start time value of "{0}" [type:{1}]'.format( value, type( value ) ) )
            
    if isinstance( time_value, int ):
        # convert integer UNIX timestamp to a date-time value
        time_value = datetime.fromtimestamp( time_value , utc )
        
    if time_value.tzinfo:
        # Convert a localized time to localized UTC
        time_value = time_value.astimezone( utc )
    else:
        # Convert naive time to a localized time
        time_value = utc.localize( time_value )
        
    return time_value





    
