# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import yaml, json, pytz
from datetime                          import datetime, date
from coils.core                        import *
from coils.foundation                  import Parse_Value_To_UTCDateTime
from coils.net.foundation              import StaticObject
from coils.net                         import DAVFolder, OmphalosCollection
from signalobject                      import SignalObject
from workflow                          import WorkflowPresentation
from scheduleobject                    import ScheduleObject

class ScheduleFolder(DAVFolder, WorkflowPresentation):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self.payload = None

    def supports_PUT(self):
        return True

    def _load_contents(self):
        if isinstance(self.payload, list):
            return True
        self.payload = self.context.run_command('workflow::get-schedule', raise_error=True, timeout=60)
        if isinstance( self.payload, list ):
            self.log.debug( 'Found {0} workflow schedule entries'.format( len( self.payload ) ) )
            for entry in self.payload:
                name = '{0}.json'.format(entry['UUID'])
                self.insert_child(name, ScheduleObject(self, name, parameters=self.parameters,
                                                                   request=self.request,
                                                                   context=self.context,
                                                                   entry = entry) ) 
            return True
        return False

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        
        def _encode(o):
            if (isinstance(o, datetime)):
                return  o.strftime('%Y-%m-%dT%H:%M:%S')
            raise TypeError()
            
        if self.load_contents():
            if self.has_child(name, supports_aliases=False):
                return self.get_child(name, supports_aliases=False)
            elif name in ( '.contents' ):
               return StaticObject(self, '.json', context=self.context,
                                                  request=self.request,
                                                  payload=json.dumps(self.payload, default=_encode),
                                                  mimetype='application/json')
        raise self.no_such_path()

    def do_PUT(self, request_name):
        """ Allows schedule entries to be made via PUT """
            
        payload = self.request.get_request_payload( )
        try:
            args_in    = json.loads( payload )
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('JSON deserialization failed, input {0} bytes'.format( len( payload ) ) )
            
        args = ScheduleFolder.Parse_Schedule_Arguements( args_in )
        
        self.log.info( '******** Calling' ) 
        
        job_id = self.context.run_command( 'process::schedule', **args )
        
        self.log.info( '******** Workflow schedular entry "{0}" created via WebDAV'.format( job_id ) )
        
        if job_id:
            self.request.simple_response( 201, headers= {
                                                 'Location': u'/dav/Workflow/Schedule/{0}.json'.format( job_id ),
                                                 'X-OpenGroupware-ScheduleEntryUUID': job_id,
                                               } )
        else:
            raise CoilsException( 'Unable to create schedule entry' )
            
        self.log.error( '*******************END*****************************' )

    @staticmethod
    def Parse_Schedule_Arguements( args_in ):
        args_out = { }
        if 'routeId'        in args_in: 
            args_out['route_id'] = int( args_in[ 'routeId' ] )
        else:
            raise CoilsException( 'No routeId specified in scheduling request' )
            
        if 'priority'       in args_in: args_out['priority']   = int( args_in['priority'] )
        if 'contextId'      in args_in: args_out['context_id'] = int( args_in[ 'contextId' ] )
        if 'repeat'         in args_in: args_out['repeat']     = int( args_in[ 'repeat' ] )
        if 'attachmentUUID' in args_in: args_out['attachmentUUID'] = unicode( args_in[ 'attachmentUUID' ] )
        
        #xattrDict
        if 'xattrDict' in args_in:
            xattr_dict = { }
            for key, value in args_in[ 'xattrDict' ].items( ):
                if isinstance( key, basestring ) and len ( key ) < 128:
                    if ( isinstance( value, basestring ) or
                         isinstance( value, int ) or
                         isinstance( value, float ) ):
                        xattr_dict[ key ] = value
                    else:
                        raise CoilsException( 'Unsupport XATTR value type "{0}"'.format( type( value ) ) )
                else:
                    raise CoilsException( 'Unsupported XATTR name "{0}"'.format( type( key ) ) )
            args_out[ 'xattrDict' ] = xattr_dict
        
        if 'type' not in args_in:
            raise CoilsException( 'No scheduling entry type specified in scheduling request' )
        elif args_in[ 'type' ] == 'simple':
            # Simple
            if 'date' in args_in:
                args_out[ 'date' ] = Parse_Value_To_UTCDateTime( time_value = args_in.get( 'date' ) )
            else:
                raise CoilsException( 'Simple scheduling type requested with no "date" specified.' )
        elif args_in['type' ] == 'interval':
            # Interval
            args_out[ 'weeks' ]   = int( args_in.get('weeks', 0 ) )
            args_out[ 'days' ]    = int( args_in.get('days', 0 ) )
            args_out[ 'hours' ]   = int( args_in.get('hours', 0 ) )
            args_out[ 'minutes' ] = int( args_in.get('minutes', 0 ) )
            args_out[ 'seconds' ] = int( args_in.get('seconds', 0 ) )
            if ( not args_out[ 'weeks' ] and not args_out[ 'days' ] and
                 not args_out[ 'hours' ] and not args_out[ 'minutes' ] and
                 not args_out[ 'seconds' ] ):
                raise CoilsException( 'No interval values specified for "interval" schedule type.' )
            args_out[ 'start' ]   = Parse_Value_To_UTCDateTime( time_value = args_in.get( 'date', None ), 
                                                                default    = datetime.utcnow( ) )
        elif args_in[ 'type' ] == 'cron':
            # Cron
            args_out[ 'year' ]        = str( args_in.get('year', '*' ) )
            args_out[ 'month' ]       = str( args_in.get('month', '*' ) )
            args_out[ 'day' ]         = str( args_in.get('day', '*' ) )
            args_out[ 'weekday' ]     = str( args_in.get('weekday', '*' ) )
            args_out[ 'hour' ]        = str( args_in.get('hour', '*' ) )
            args_out[ 'minute' ]      = str( args_in.get('minute', '*' ) )
        else:
            # raise exception
            raise CoilsException( 'Unsupported scheduler entry type "{0}"'.format( args_in[ 'type' ] ) )
        args_out[ 'type' ] = args_in[ 'type' ]   
        
        return args_out 
