#!/usr/bin/env python
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import base64, logging
from time import time
from datetime import date, datetime
from coils.core import CoilsException
from coils.foundation                  import Parse_Value_To_UTCDateTime

'''
 { "dayOfWeek": "3,6",
   "week": "*",
   "nextIteration": "2012-11-15T23:00:00",
   "month": "*",
   "second": "0",
   "routeName": "TRInvoiceRegisterCollector",
   "year": "*",
   "day": "*",
   "minute": "0",
   "attachmentUUID": null,
   "xattrDict": {"start": "$__MONTHSTART__;", "end": "$__OMPHALOSDATE__;"},
   "contextId": 15211340,
   "UUID": "{1bd14aab-a95a-430e-aa57-6d879133d619}",
   "hour": "23",
   "routeId": 70478879,
   "priority": 200,
   "iterationsPerformed": 8,
   "iterationsRemaining": -1,
   "type": "cron"}
'''

def represent_value(value, null=''):
    if value is None:
        return null
    return value

def render_workflow_schedule_entry( schedule_entry ):
    """
    Create an Omphalosy representation of a workflow schedule entry.
    """

    result = {
               'UUID':                represent_value( schedule_entry[ 'UUID' ] ),
               'routeName':           represent_value( schedule_entry[ 'routeName' ] ),
               'attachmentUUID':      represent_value( schedule_entry[ 'attachmentUUID' ] ),
               'contextObjectId':     represent_value( schedule_entry[ 'contextId' ], null=0 ),
               'routeObjectId':       represent_value( schedule_entry[ 'routeId' ], null=0 ),
               #'repeatCount':         represent_value( schedule_entry[ 'repeat' ] ),
               'priority':            represent_value( schedule_entry[ 'priority' ], null=200 ),
               'nextIteration':       represent_value( schedule_entry[ 'nextIteration' ] ),
               'iterationsPerformed': represent_value( schedule_entry[ 'iterationsPerformed' ], null=0 ),
               'iterationsRemaining': represent_value( schedule_entry[ 'iterationsRemaining' ], null=0 ),
               '_SCHEDULE':           [ ],
               '_XATTRS':             [ ],
               'entityName':          'scheduleEntry'
             }

    if schedule_entry[ 'xattrDict' ]:
        for key, value in schedule_entry[ 'xattrDict' ].items( ):
            result[ '_XATTRS' ].append( { 'entityName': 'workflowXATTR',
                                          'xattrKey':   key,
                                          'xattrValue': value } )

    if schedule_entry[ 'type' ] == 'cron':
        result[ '_SCHEDULE' ].append( { 'entityName': 'cronRecord',
                                        'parentUUID': schedule_entry[ 'UUID' ],
                                        "dayOfWeek":  schedule_entry[ 'dayOfWeek' ],
                                        "week":       schedule_entry[ 'week' ],
                                        "month":      schedule_entry[ 'month' ],
                                        "second":     schedule_entry[ 'second' ],
                                        #"year":       schedule_entry[ 'year' ],
                                        "day":        schedule_entry[ 'day' ],
                                        "minute":     schedule_entry[ 'minute' ],
                                      } )
    elif schedule_entry[ 'type' ] == 'interval':
        result[ '_SCHEDULE' ].append( { 'entityName':     'intervalRecord',
                                        'parentUUID':     schedule_entry[ 'UUID' ],
                                        'intervalPeriod': schedule_entry[ 'interval' ],
                                        'startDate':      schedule_entry[ 'start' ],
                                      } )
    elif schedule_entry[ 'type' ] == 'simple':
        result[ '_SCHEDULE' ].append( { 'entityName': 'simpleRecord',
                                        'parentUUID': schedule_entry[ 'UUID' ],
                                        'date':       schedule_entry[ 'date' ],
                                      } )
    else:
        # TODO: raise an unreachable code-point exception
        pass

    return result


def render_workflow_schedule( schedule_entries ):
    '''
    Render a list of schedule entries into a list of Omphalos representations

    :param schedule_entries: a list of schedule entrues in native format
    '''
    result = [ ]
    for schedule_entry in schedule_entries:
        result.append( render_workflow_schedule_entry( schedule_entry ) )
    return result

def parse_workflow_schedule_entry( schedule_entry, context ):
    """
    Parse an Omphalos schedule representation into a native representation
    """

    result = {
               'route_id':        int( schedule_entry.get( 'routeObjectId', 0 ) ),
               'context_id':      int( schedule_entry.get( 'contextObjectId', context.account_id ) ),
               'attachmentUUID': schedule_entry.get( 'attachmentUUID', '' ),
               'priority':       int( schedule_entry.get( 'priority', 201 ) ),
             }

    repeat = int( schedule_entry.get( 'repeatCount', 0 ) )
    if repeat > 0:
        result[ 'repeat' ] = repeat

    if not result[ 'route_id' ]:
        raise CoilsException( 'Schedule entry must specify a route.' )

    if not result[ 'context_id' ]:
        raise CoilsException( 'Schedule entry must specify a context.' )

    schedule_details = schedule_entry[ '_SCHEDULE' ]
    if schedule_details:
        schedule_details = schedule_details[ 0 ]
        if schedule_details[ 'entityName' ] == 'cronRecord':
            # Cron
            #result[ 'year' ]    = str( schedule_details.get('year', '*' ) )
            result[ 'type' ]    = u'cron'
            result[ 'month' ]   = str( schedule_details.get('month', '*' ) )
            result[ 'day' ]     = str( schedule_details.get('day', '*' ) )
            result[ 'weekday' ] = str( schedule_details.get('weekday', '*' ) )
            result[ 'hour' ]    = str( schedule_details.get('hour', '*' ) )
            result[ 'minute' ]  = str( schedule_details.get('minute', '*' ) )
            # Make sure some pattern was specified, otherwise this evaluates to every-moment
            if ( result[ 'weekday' ] == '*' and result[ 'month' ] == '*' and
                 result[ 'day' ] == '*'     and result[ 'weekday' ] == '*' and
                 result[ 'hour' ] == '*'    and result[ 'minute' ] == '*' ):
                raise CoilsException( 'No pattern values specified for "cron" schedule type.' )
        elif schedule_details[ 'entityName' ] == 'intervalRecord':
            # Interval
            result[ 'type' ]    = u'interval'
            result[ 'weeks' ]   = int( schedule_details.get('weeks', 0 ) )
            result[ 'days' ]    = int( schedule_details.get('days', 0 ) )
            result[ 'hours' ]   = int( schedule_details.get('hours', 0 ) )
            result[ 'minutes' ] = int( schedule_details.get('minutes', 0 ) )
            result[ 'seconds' ] = int( schedule_details.get('seconds', 0 ) )
            # Make sure some value was specified, we do not support an interval of zero
            if ( not result[ 'weeks' ] and not result[ 'days' ] and
                 not result[ 'hours' ] and not result[ 'minutes' ] and
                 not result[ 'seconds' ] ):
                raise CoilsException( 'No interval values specified for "interval" schedule type.' )
            result[ 'start' ] = Parse_Value_To_UTCDateTime( time_value = schedule_details.get( 'date', None ),
                                                            default    = datetime.utcnow( ) )
        elif schedule_details[ 'entityName' ] == 'simpleRecord':
            result[ 'type' ]    = u'simple'
            result[ 'date' ] = Parse_Value_To_UTCDateTime( time_value = schedule_details.get( 'date' ) )
            # Make sure a date was required, that is mandatory
            if not result[ 'date' ]:
                raise CoilsException( 'No date specified for "simple" schedule type.' )
    else:
        # As no schedule details were provided we wipe the type, this stanza
        # is now only useful for processing as a delete request
        result[ 'type' ] = None

    xattr_dict = { }
    for xattr in schedule_entry.get( '_XATTRS', [ ] ):
        xattr_dict[ xattr[ 'xattrKey'] ] = xattr[ 'xattrValue' ]
    result[ 'xattrs' ] = xattr_dict

    return result
