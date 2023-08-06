#!/usr/bin/python
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from StringIO import StringIO

# WARNING: Does *not* support Binary / NSData values!
# Updated in Unicode branch (2010-05) to support unicode strings.
# OpenSTEP plist files are expected to be ISO8859-2
class PListWriter:

    def __init__(self):
        self.buf = StringIO()

    def store(self, payload):
        self.buf.write(u'{\n')
        self.indent = 0
        if (isinstance(payload, dict)):
            for key in payload.keys():
                self._append(key, payload[key])
        self.buf.write(u'}')
        return self.buf.getvalue()

    def _requires_quoting(self, value):
        if (isinstance(value, basestring)):
            if (value.isalnum()):
                return False
            return True
        raise 'Only string values can be quoted.'

    def _append(self, key, value):
        self._inc_indent()
        self._append_key(key)
        if (isinstance(value, basestring)):
            self._append_string(value)
        elif (isinstance(value, int)):
            self._append_integer(value)
        elif (isinstance(value, list)):
            self._append_array(value)
        elif (isinstance(value, dict)):
            self._append_dictionary(value)
        else:
            raise 'Unsupported type in plist'
        self._append_suffix()
        self._dec_indent()

    def _inc_indent(self):
        self.indent = self.indent + 1

    def _dec_indent(self):
        self.indent = self.indent - 1

    def _append_indent(self):
        count = 0
        while (count < self.indent):
            self.buf.write('    ')
            count = count + 1

    def _append_suffix(self):
        self.buf.write(u';\n')

    def _append_key(self, key):
        self._append_indent()
        if (self._requires_quoting(key)):
            self.buf.write(u'"%s" = ' % key)
        else:
            self.buf.write(u'%s = ' % key)

    def _append_string(self, value):
        if (self._requires_quoting(value)):
            # Quote double quotes with a slash
            self.buf.write(u'"%s"' % value.replace('\x22', '\x5c\x22'))
        else:
            self.buf.write(value)

    def _append_integer(self, value):
        self.buf.write(u'%d' % value)

    def _append_array(self, value):
        self.buf.write(u'(\n')
        self._inc_indent()
        i = 0
        while (i < len(value)):
            self._append_indent()
            x = value[i]
            if (isinstance(x, basestring)):
                self._append_string(x)
            elif (isinstance(x, int)):
                self._append_integer(x)
            elif (isinstance(x, list)):
                self._append_array(x)
            elif (isinstance(x, dict)):
                self._append_dictionary(x)
            i = i + 1
            if (i <len(value)):
                self.buf.write(u',\n')
            else:
                self.buf.write(u'\n')

        self._dec_indent()
        self._append_indent()
        self.buf.write(u')')

    def _append_dictionary(self, value):
        self.buf.write(u'{\n')
        i = 0
        while (i < len(value.keys())):
            k = value.keys()[i]
            v = value[k]
            self._append(k, v)
            i = i + 1
        self._append_indent()
        self.buf.write('}')
