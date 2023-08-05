#
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
#
import calendar
from datetime import datetime, date, timedelta
from dateutil.rrule import rrule, MO, TU, WE, TH, FR, DAILY
from coils.logic.workflow.tables import Table
 
class OIEXSLTExtensionPoints:
    
    def __init__(self, process, context, scope, ctxids):
        self.process = process
        self.context = context
        self.scope   = scope
        self.ctxids  = ctxids
        self.tables  = { }

    def shutdown(self):
        for name, table in self.tables.items():
            table.shutdown()

    def _make_date(self, value, method, param):
        value = value.strip()
        if len(value) == 10:
            value = datetime.strptime(value, '%Y-%m-%d')
        elif len(value) == 19:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            raise CoilsException( '{0} received value {1} which is not a StandardXML formatted date: "{2}"'.format( method, param, value ) )
        return value

    def _get_sequence_value(self, scope, name):
        
        sequence_target = None
        if scope == 'process':
            sequence_target = self.process
        elif scope == 'route':
            sequence_target = self.process.route
        elif scope == 'global':
            raise NotImplementedException()
        else:
            raise CoilsException('Invalid execution path! Possible security model violation.')
        
        if not sequence_target:
            raise CoilsException('Unable to determine the target for scope of sequence "{0}"'.format(name))
            
        name = 'sequence_{0}'.format(name)                
            
        prop = self.context.property_manager.get_property(sequence_target, 'http://www.opengroupware.us/oie', name)
            
        if prop:
            value = prop.get_value()
            try:
                value = long(value)
            except:
                error = 'Workflow sequence value is corrupted: sequence={0} value="{1}" scope={2}'.format(name, value, scope)
                raise CoilsException(error)
            return value
        else:
            raise CoilsException('No such sequence as "{0}" in scope "{1}" for processId#{2}.'.format(name, scope, self.process.object_id))            
            
    def _set_sequence_value(self, scope, name):
        
        sequence_target = None
        if scope == 'process':
            sequence_target = self.process
        elif scope == 'route':
            sequence_target = self.process.route
        elif scope == 'global':
            raise NotImplementedException()
        else:
            raise CoilsException('Invalid execution path! Possible security model violation.')
        
        if not sequence_target:
            raise CoilsException('Unable to determine the target for scope of sequence "{0}"'.format(name))        
            
        name = 'sequence_{0}'.format(name)
            
        self.context.property_manager.set_property(sequence_target, 'http://www.opengroupware.us/oie', name, long(value))            

    def sequencevalue(self, _, scope, name):
        # TODO: Test
        return self._get_sequence_value(scope, name)

    def sequencereset(self, _, scope, name, value):
        # TODO: Test
        self._set_sequence_value(scope, name, value)

    def sequenceincrement(self, _, scope, name, increment):
        # TODO: Test
        value = self._get_sequence_value(scope, name)
        value += increment
        self._set_sequence_value(scope, name, value)
        return unicode(value)
        
    def messagetext(self, _, label):
        data = self.context.run_command('message::get-text', process=self.process,
                                                             scope=self.scope,
                                                             label=label)
        if not data:
            return ''
        return data
                
    def _search_for_objects(self, domain, args):
        criteria = [ ]
        while len(args) > 0:
            criteria.append( { 'key': args.pop(0), 'value': args.pop(0) } )
        result = self.context.run_command('{0}::search'.format(domain), criteria=criteria, 
                                                                        contexts=self.ctxids )
        return result

    def searchforobjectid(self, _, domain, *args):
        result = self._search_for_objects(domain, list(args))
        if len(result) == 1:
            result = result[0]
            if hasattr(result, 'object_id'):
                return unicode(result.object_id)
        return ''

    def countobjects(self, _, domain, *args):
        result = self._search_for_objects(domain, list(args))
        return unicode(len(result))

    def tablelookup(self, _, name, *values):
        if name not in self.tables:
            self.tables[ name ] = Table.Load( name )
        table = self.tables[ name ]
        table.setup( context = self.context, process=self.process, scope=self.scope)
        return unicode(table.lookup_value( values ) )
        
    def reformatdate(self, _, value, format):
        value = self._make_date( value, 'reformatdate', 'date' )
        return value.strftime(format)
        
    def datetimetodate(self, _, value):
        value = value.strip()
        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value.strftime('%Y-%m-%d')
        
    def stringtodate(self, _, value, format):
        value = value.strip()
        value = datetime.strptime(value.strip(), format)
        return value.strftime('%Y-%m-%d') 

    def stringtodatetime(self, _, value, format):
        value = value.strip()
        value = datetime.strptime(value.strip(), format)
        return value.strftime('%Y-%m-%d %H:%M:%S')
        
    def xattrvalue(self, _, name):
        name = name.strip().lower()
        prop = self.context.property_manager.get_property(self.process,
                                                          'http://www.opengroupware.us/oie',
                                                          'xattr_{0}'.format(name))
        if prop:
            return unicode( prop.get_value( ) )
        return u''
        
    def getpid(self, _ ):
        return unicode( self.process.object_id )

    def month(self, _, value ):
        value = datetime.strptime( value.strip( ), '%Y-%m-%d' )
        return unicode( value.month )

    def year(self, _, value ):
        value = datetime.strptime( value.strip( ), '%Y-%m-%d' )
        return unicode( value.year )
        
    def monthstart( self, _, year, month ):
        
        try: year = int( year ) 
        except: raise CoilsException( 'Non-numeric year provided to oie:monthstart' )
        
        try: month = int( month ) 
        except: raise CoilsException( 'Non-numeric month provided to oie:monthstart' )
        
        return date( year=year, month=month, day=1 ).strftime( '%Y-%m-%d' )
        
    def monthend( self, _, year, month ):
        day = calendar.monthrange(year, month)[1]
        return date( year=year, month=month, day=day ).strftime( '%Y-%m-%d' )        

    def today(self, _, ):
        return date.today( ).strftime( '%Y-%m-%d' )

    def dateplusdays(self, _, start, delta):
        start = datetime.strptime( start.strip( ), '%Y-%m-%d' )
        result = start + timedelta( days=int( delta ) )
        return result.strftime( '%Y-%m-%d' )
        
    def yesterday(self, _):
        return (date.today() + timedelta(days=-1)).strftime('%Y-%m-%d')

    def tomorrow(self, _):
        return (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
    def days(self, _, start, end):
        start = self._make_date( start, 'days', 'start' )
        end   = self._make_date( end,   'days', 'end' )
        return (end - start).days
        
    def weekdays(self, _, start, end):
        start = self._make_date( start, 'weekdays', 'start' )
        end   = self._make_date( end,   'weekdays', 'end' )        
        rule = rrule( DAILY, byweekday=( MO, TU, WE, TH, FR ), dtstart=start, until=end )
        return unicode( rule.count( ) )
        
    def replace(self, _, value, text1, text2):
        if isinstance( value, list ):
            if not value:
                return ''
            value = value[ 0 ]
        return value.replace( text1, text2 )
        
