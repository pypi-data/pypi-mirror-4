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
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

class AddColumnAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "add-column"
    __aliases__   = [ 'addColumn', 'addColumnAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        self.rfile.seek(0)
        table_name = None
        format_name = None
        format_class = None
        for event, element in etree.iterparse(self.rfile, events=("start",)):
          if (event == 'start' and element.tag == 'ResultSet'):
            table_name   = element.attrib.get('tableName')
            format_name  = element.attrib.get('formatName')
            format_class = element.attrib.get('className')
            element.clear()
            break
        self.wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        self.wfile.write(u'<ResultSet formatName="{0}" className="{1}" tableName="{2}">'.\
            format(format_name, format_class, table_name))
        self.rfile.seek(0)
        for event, element in etree.iterparse(self.rfile, events=("end",)):
            if (event == 'end') and (element.tag == 'row'):
                z = etree.Element(self._name)
                z.attrib['dataType']     = self._type
                z.attrib['isNull']       = self._null
                z.attrib['isPrimaryKey'] = self._pkey
                z.text = self._value
                element.append(z)
                self.wfile.write(etree.tostring(element))
                element.clear()
        self.wfile.write(u'</ResultSet>')

    def parse_action_parameters(self):
        self._name  = self.action_parameters.get('name')
        self._type  = self.action_parameters.get('dataType', 'string')
        self._null  = self.action_parameters.get('isNull', 'false').lower()
        self._pkey  = self.action_parameters.get('isPrimaryKey', 'false').lower()
        self._value = self.action_parameters.get('value', '')
        self._name  = self.process_label_substitutions(self._name)
        self._value = self.process_label_substitutions(self._value)

    def do_epilogue(self):
        pass
