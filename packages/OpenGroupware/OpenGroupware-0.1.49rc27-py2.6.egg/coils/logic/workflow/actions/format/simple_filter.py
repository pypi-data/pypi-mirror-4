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
#
import string
from StringIO            import StringIO
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

class SimpleFilter(ActionCommand):
    __domain__ = "action"
    __operation__ = "simple-filter"
    __aliases__   = [ 'simpleFilter', 'simpleFilterAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        summary = StringIO('')
        self._row_in = 0
        self._row_out = 0
        try:
            StandardXML.Filter_Rows(self._rfile, self._wfile, callback=self.callback)
        finally:
            summary.write(u'\n  Rows input = {0}, Rows output = {1}'.format(self._row_in, self._row_out))
            self.log_message(summary.getvalue(), category='info')

    def callback(self, row):
        self._row_in += 1
        keys, fields = StandardXML.Parse_Row(row)
        # Get field value from row
        if self._field_name in keys:
            x = keys[self._field_name]
        elif self._field_name in fields:
            x = fields[self._field_name]
        else:
            raise CoilsException('Field {0} not found in input record.'.format(self._field_name))
        # Compare Values
        if  self._expression == 'EQUALS':
            if (x == self._compare_value):
                self._row_out += 1
                return True
            return False
        elif self._expression == 'NOT-EQUALS':
            if (x != self._compare_value):
                self._row_out += 1
                return True
            return False
        else:
            raise CoilsException('Unknown comparision expression: {0}'.format(self._compare_value))

    def parse_action_parameters(self):
        self._field_name      = self._params.get('fieldName', None)
        self._expression      = self._params.get('expression', 'EQUALS').upper()
        self._cast_as         = self._params.get('castAs', 'STRING').upper()
        self._compare_value   = self._params.get('compareValue', None)
        if (self._field_name is None):
            raise CoilsException('No field name specified for comparison.')
        if (self._compare_value is None):
            raise CoilsException('No comparison expression specified')
        # Perform requested cast of compare value
        if (self._cast_as == 'INTEGER'):
            self._compare_value = int(self._compare_value)
        elif (self._cast_as == 'FLOAT'):
            self._compare_value = float(self._compare_value)
        elif (self._cast_as == 'UNICODE'):
            self._compare_value = unicode(self._compare_value)