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
# THE SOFTWARE.
#
from itertools import izip
from coils.core               import CoilsException
from namespaces               import XML_NAMESPACE, ALL_PROPS, REVERSE_XML_NAMESPACE

def introspect_properties(target):
    namespaces = { 'http://apache.org/dav/props/':   'A',
                   'urn:ietf:params:xml:ns:caldav':  'C',
                   'DAV:':                           'D',
                   'urn:ietf:params:xml:ns:carddav': 'E',
                   'http://groupdav.org/':           'G',
                 }
    properties = []
    nm_ordinal = 74
    methods = [ method for method in dir(target) if method.startswith('get_property_')]
    for method in methods:
        parts = method.split('_', 3)
        if (len(parts) == 4):
            # Filter out unknown namespace properties
            if (parts[2] != 'unknown'):
                namespace = REVERSE_XML_NAMESPACE.get(parts[2], 'DAV')
                if (namespace.upper() == 'DAV'):
                    prefix = 'D'
                elif namespace in namespaces:
                    prefix = namespaces[namespace]
                else:
                    prefix = chr(nm_ordinal)
                    namespaces[namespace] = prefix
                    nm_ordinal += 1
                element = parts[3].replace('_', '-')
                properties.append( ( method,
                                     namespace,
                                     element,
                                     parts[2],
                                     '{0}:{1}'.format(prefix, element) ) )
    keys = namespaces.iterkeys()
    values = namespaces.itervalues()
    namespaces = dict(izip(values, keys))
    return properties, namespaces