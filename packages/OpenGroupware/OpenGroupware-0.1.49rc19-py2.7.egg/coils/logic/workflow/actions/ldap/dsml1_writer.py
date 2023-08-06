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
import string, base64
from xml.sax.saxutils import escape

DSML_EXCLUDED_ATTRIBUTES = [ 'objectClass', 'objectcass' ]

class DSML1Writer(object):

    def __init__(self):
        self._wfile = None

    def _write_objectclasses(self, entry):
        objectclasses = entry.get('objectClass',entry.get('objectclass',[]))
        if (len(objectclasses) > 0):
            self._wfile.write(u'<dsml:objectclass>')
            for oc in objectclasses:
                self._wfile.write(u'<dsml:oc-value>{0}</dsml:oc-value>'.format(oc))
            self._wfile.write(u'</dsml:objectclass>')

    def _write_attribute(self, attribute, values):
        self._wfile.write('<dsml:attr name="{0}">'.format(attribute))
        for value in values:
            try:
                text = unicode(value, 'utf-8')
            except UnicodeError:
                text = base64.encodestring(value)
                self._wfile.write(u'<dsml:value encoding="base64">{0}</dsml:value>'.format(text))
            else:
                self._wfile.write(u'<dsml:value>{0}</dsml:value>'.format(escape(text)))
        self._wfile.write(u'</dsml:attr>')

    def _write_attributes(self, entry):
        attributes = entry.keys()[:]
        attributes.sort()
        for attribute in attributes:
            if (attribute not in DSML_EXCLUDED_ATTRIBUTES):
                self._write_attribute(attribute, entry[attribute])

    def _write_entry(self, entry):
        self._wfile.write(u'<dsml:entry dn="{0}">'.format(escape(entry[0])))
        self._write_objectclasses(entry[1])
        self._write_attributes(entry[1])
        self._wfile.write(u'</dsml:entry>')

    def write(self, data, stream):
        self._wfile = stream
        self._wfile.write(u'<?xml version="1.0" encoding="utf-8"?>')
        self._wfile.write(u'<dsml:dsml xmlns:dsml="http://www.dsml.org/DSML">')
        self._wfile.write(u'<dsml:directory-entries>')
        if (isinstance(data, list)):
            for entry in data:
                self._write_entry(entry)
        else:
            self._write_entry(data)
        self._wfile.write(u'</dsml:directory-entries>')
        self._wfile.write(u'</dsml:dsml>')
