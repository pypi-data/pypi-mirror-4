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
import os, re
from coils.core          import *
from coils.core.logic    import ActionCommand

class FindAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "re-find"
    __aliases__   = [ 'regularExpressionFind', 'regularExpressionFindAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        self.log.debug('Expression: {0}'.format(self._expression))
        text = self.rfile.read()
        try:
            result = re.findall(self._expression, text)
        except Exception, e:
            self.log.error('Failure processing regular expression')
            self.log.exception(e)
            raise e

        if (len(result)):
            if self._singleton:
                result = result[0]
                if self._strip_value:
                    result = result.strip()
                self.wfile.write(result)
            else:
                # multiple-result-mode
                self.wfile.write(u'<?xml version="1.0" encoding="utf-8"?>')
                self.wfile.write(u'<ResultSet>')
                for value in result:
                    if self._strip_value:
                        value = value.strip()
                    self.wfile.write(u'<value>{0}</value>'.format(self.encode_text(value)))
                self.wfile.write(u'</ResultSet>')
        else:
            if self._singleton:
                # multiple-result-mode
                self.wfile.write(u'<?xml version="1.0" encoding="utf-8"?>')
                self.wfile.write(u'<ResultSet/>')

    def parse_action_parameters(self):
        self._expression  = self.action_parameters.get('expression', None)
        self._strip_value = self.action_parameters.get('trimValue', 'NO')
        # TODO: This is dumb; it should be YES/NO like every other toggle
        self._singleton   = self.action_parameters.get('singleton', 'YES').upper()
        if (self._expression is None):
            raise CoilsException('No expression specified for re action')
        self._expression = self.decode_text(self._expression)
        self._expression = self.process_label_substitutions(self._expression)

        if self._strip_value.upper() == 'YES':
            self._strip_value = True
        else:
            self._strip_value = False

        if self._singleton.upper() in ['YES', 'TRUE']:
            self._singleton = True
        else:
            self._singleton = False
