#
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
#
import re, datetime
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

class RowTemplateAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "row-template"
    __aliases__   = [ 'rowTemplate', 'rowTemplateAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        rows = StandardXML.Read_Rows(self.rfile)
        for row in rows:
            text = self._template
            fields = row[0] # keys
            fields.update(row[1]) # non-key fields
            #labels = set(re.findall('{:[A-z]*}', text))
            labels = re.findall('{:[A-z].[A-z0-9=:,]*}', text)
            for label in labels:
                components = label[2:-1].split(':')
                #name = label[2:-1]
                name = components[0]
                params = { }
                if (len(components) > 1): kind = components[1].lower()
                if (len(components) > 2):
                    for param in components[2].lower().split(','):
                        params[param.split('=')[0]] = param.split('=')[1]
                else: kind = 's'
                if name in fields:
                    value = fields[name]
                    if (kind in ['string', 's']):
                        if (isinstance(value, datetime.datetime)):
                            value = value.strftime(self._dt_format)
                        elif (isinstance(value, float)):
                            if ('precision' in params):
                                value = u'%.*f' % (int(params['precision']), value)
                            else:
                                value = unicode(value)
                        else:
                            value = unicode(value)
                        if 'ljust' in params:
                            value = value.ljust(int(params['ljust']))
                        elif 'rjust' in params:
                            value = value.rjust(int(params['rjust']))
                        elif 'center' in params:
                            value = value.center(int(params['center']))

                    text = text.replace(label, value)
            self.wfile.write(text)

    @property
    def result_mimetype(self):
        return self._mime_type

    def parse_action_parameters(self):
        self._template  = self.action_parameters.get('template')
        self._dt_format = self.action_parameters.get('datetimeFormat', '%Y-%m-%d')
        self._mime_type = self.action_parameters.get('mimeType', 'text/plain')
        self._template  = self.process_label_substitutions(self._template)

    def do_epilogue(self):
        pass
