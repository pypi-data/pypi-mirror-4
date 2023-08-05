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
import base64, json, StringIO
from lxml import etree
from xml.sax.saxutils    import escape, unescape
from coils.core          import *
from coils.core.logic    import ActionCommand


def fix_key(key):
    if key[0:1].isdigit():
        key = 'key' + key
    return key


def describe_key_value(key, value):
    key = fix_key(key)
    if (value is None):
        return u'<{0}/>'.format(key)
    elif (isinstance(value, dict)):
        return u'<{0} dataType="complex">{1}</{0}>'.format(key, describe_dict(value))
    elif (isinstance(value, list)):
        return u'<{0} dataType="list">{1}</{0}>'.format(key, describe_list(value))
    else:
        return u'<{0}>{1}</{0}>'.format(key, escape(str(value)))


def describe_list(values):
    stream = StringIO.StringIO()
    for value in values:
        if (value is None):
            stream.write(u'<value/>')
        elif (isinstance(value, dict)):
            stream.write(u'<value dataType="complex">{0}</value>'.format(describe_dict(value)))
        elif (isinstance(value, list)):
            stream.write(u'<value dataType="list">{0}</value>'.format(describe_list(value)))
        else:
            stream.write(u'<value>{0}</value>'.format(escape(str(value))))
    payload = stream.getvalue()
    stream.close()
    return payload


def describe_dict(collection):
    stream = StringIO.StringIO()
    for key in collection:
        value = collection[key]
        key = fix_key(key)
        if (value is None):
            stream.write(u'<{0}/>'.format(key))
        elif (isinstance(value, dict)):
            stream.write(u'<{0} dataType="complex">{1}</{0}>'.format(key, describe_dict(value)))
        elif (isinstance(value, list)):
            stream.write('<{0} dataType="list">{1}</{0}>'.format(key, describe_list(value)))
        else:
            stream.write(u'<{0}>{1}</{0}>'.format(key, escape(str(value))))
    payload = stream.getvalue()
    stream.close()
    return payload


class ReadJSONAction(ActionCommand):
    ''' ReadJSONActon accepts JSON data as its input message and transforms it to StandardXML. '''
    __domain__ = "action"
    __operation__ = "read-json"
    __aliases__   = [ 'readJSON', 'readJSONAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def parse_action_parameters(self):
        self._xpath    = self.action_parameters.get('xpath', None)
        self._b64      = self.action_parameters.get('isBase64', 'NO').upper()

    def do_action(self):
        if (self._xpath is None):
            # Filter decoding; input message is raw JSON
            self.log.debug('Starting JSON decoding')
            data = json.load(self.rfile)
            self.log.debug('JSON data decoded')
            self.wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
            self.wfile.write(u'<json>')
            if (isinstance(data, dict)):
                self.wfile.write('<value dataType="complex">{0}</value>'.format(describe_dict(data)))
            elif (isinstance(data, list)):
                self.wfile.write('<value dataType="list">{0}</value>'.format(describe_list(data)))
            else:
                self.wfile.write(u'<value>{1}</value>'.format(escape(str(value))))
            self.wfile.write(u'</json>')
        else:
            # XPath replacement; Replace a JSON section of an XML document with XML
            doc = etree.parse(self.rfile)
            jsondata = doc.xpath(self._xpath)[0]
            text = jsondata.text
            data = json.loads(text)
            if (isinstance(data, dict)):
                text = u'<json><value dataType="complex">{0}</value></json>'.format(describe_dict(data))
            elif (isinstance(data, list)):
                text = u'<json><value dataType="list">{0}</value></json>'.format(describe_list(data))
            else:
                text = u'<json><value>{0}</value></json>'.format(escape(str(value)))
            xml = etree.fromstring(text)
            text = None
            doc.getroot().replace(jsondata, xml)
            self.wfile.write(etree.tostring(doc))
            doc = None
            xml = None
            jsondata = None

    def do_epilogue(self):
        pass
