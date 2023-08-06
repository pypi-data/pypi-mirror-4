#
# Copyright (c) 2011, 2012
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

class StaticLookupTable(Table):
    # TODO: Add support for a default value and optional raiseError attribute
        
    def __repr__(self):
        return '<StaticLookupTable name="{0}" count="{1}"/>'.format(self.name, len(self.c['values']))
        
    def set_description(self, description):
        self.c = description
        if 'values' not in self.c:
            raise CoilsException('StaticLookupTable does not contain the required "values" attribute.')
        if not isinstance(self.c['values'], dict):
            raise CoilsException('"value" attribute of PresenceLookupTable is a "{0}" and must be a "dict".'.format(type(self.c['values'])))
            
    def lookup_value(self, *values):
        '''
        Prepare the input value and perform the look-up
        :param value:
        '''
        
        # Tuples apparently do not expand like lists do;  Ahh, Python and your crappy types.
        args = [ ]
        for x in values:
            args.append( x )
        
        print type(values)
        key = self.cache_key_from_values( values )
        print 'KEY>>>', key
        return self.c[ 'values' ].get( key, self.c.get( 'defaultValue', None ) )
