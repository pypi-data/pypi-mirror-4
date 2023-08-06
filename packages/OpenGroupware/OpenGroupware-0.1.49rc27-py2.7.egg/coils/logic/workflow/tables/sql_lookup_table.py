#
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
#
import logging, inspect, yaml, uuid
from coils.foundation import *
from coils.core       import *
from table            import Table

class SQLLookupTable(Table):
    
    def __init__(self, context=None, process=None, scope=None):
        """
        ctor
        
        :param context: Security and operation context for message lookup
        :param process: Proccess to use when resolving message lookup
        :param scope: Scope to use when resolving message lookup
        """
                
        Table.__init__( self, context=context, process=process, scope=scope )
        
        self._db    = None
        self._cache = None
        self._hits  = 0
        self._debug = False
        self._do_input_upper = False
        self._do_input_strip = False 
        self._do_output_upper = False
        self._do_output_strip = False
        self.log = logging.getLogger('OIE.SQLLookupTable')
        
    def __repr__(self):
        return '<SQLLookupTable name="{0}" dataSource="{1}"/>'.format(self.name, self.c['SQLDataSourceName'])
        
    def set_description(self, description):
        self.c = description
        if self.c.get('useSessionCache', True): self._cache = { }
        if self.c.get('enableDebug', False):   self._debug = True
        if self.c.get('doInputUpper', False):   self._do_input_upper = True
        if self.c.get('doInputStrip', False):   self._do_input_strip = True
        if self.c.get('doOutputUpper', False):  self._do_output_upper = True
        if self.c.get('doOutputStrip', False):   self._do_output_strip = True
        if self.c.get('chainedTable', None):
            self._chained_table = Table.Load(self.c['chainedTable'])
        else:
            self._chained_table = None
                 
    def lookup_value(self, *values):
        '''
        Lookup the value using the describe SQL connection and query
        
        :param values: a referenced list of query parameter values.
        '''
        
        # Tuples apparently do not expand like lists do;  Ahh, Python and your crappy types.
        args = [ ]
        for x in values:
            args.append( x )
        
        # We avoid actually connecting to the database until an actual query is performed
        # It isn't hard to get into a case where a Table is referenced but then never used.
        if not self._db:
            self._db = SQLConnectionFactory.Connect( self.c[ 'SQLDataSourceName' ] )
              
        # Processing / Cleaning of input values
        if self._do_input_upper or self._do_input_strip:
            tmp = []
            for value in values:
                if isinstance(value, basestring):
                    if self._do_input_upper: value = value.upper()
                    if self._do_input_strip: value = value.strip()
                tmp.append(value)
            values = tuple(tmp)
            tmp = None

        # Cache check
        if self._cache:
            key = self.cache_key_from_values( values )
            if key in self._cache:
                self._hits += 1
                return self._cache[ key ]
                
        
        if self._db:
            # Database Lookup
            cursor = self._db.cursor()
            try:
                if self._debug:
                    self.log.debug('Performing table looking via "{0}"'.format(self.name))
                    self.log.debug('Values: {0}'.format( args ) )
                cursor.execute( self.c['SQLQueryText'], args )
            except Exception, e:
                self.log.error('SQL execute excetion in {0} performing "{1}"'.format(self, self.c['SQLQueryText']))
                raise e
            record = cursor.fetchone()
            if record:
                if self._debug:
                    self.log.debug( 'SQL Query found matching records' )
                result = unicode( record[ 0 ] )
            else:
                if self._debug:
                    self.log.debug( 'SQL Query found 0 matching records' )
                result = None
            cursor.close( )
            
            if result is None and self._chained_table:
                if self._debug:
                    self.log.debug( 'Passing lookup to chained table {0}'.format( self._chained_table.name ) )
                result = self._chained_table.lookup_value( *values )
                
            if result:
                if isinstance( result, basestring ):
                    if self._do_output_upper: result = result.upper( )
                    if self._do_output_strip: result = result.strip( )
                            
            # We have to make sure specifically not-None here if we just evaluate
            # self._cache as a bool then a value will never get cached since the
            # cache always starts empty and that will evaluate to false.
            if self._cache is not None:
                key = self.cache_key_from_values( values )
                self._cache[ key ] = result
                
            if self._debug:
                self.log.debug( 'Returning: {0}'.format( result ) )
                
            return result
            
        else:
            raise CoilsException( 'SQLLookup table unable to establish connection to SQLDataSource "{0}"'.format( self.c['SQLDataSourceName'] ) )
            
