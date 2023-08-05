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
from coils.foundation.api import elementflow

PROP_METHOD    = 0
PROP_NAMESPACE = 1
PROP_LOCALNAME = 2
PROP_DOMAIN    = 3
PROP_PREFIXED  = 4

def Multistatus_Response(resources=None, properties=None, stream=None, namespaces=None):
    with elementflow.xml(stream, u'D:multistatus', indent=True, namespaces=namespaces) as response:
        for resource in resources:
            with response.container('D:response'):
                response.file.write('<D:href>{0}</D:href>'.format(resource.webdav_url))
                known = {}
                unknown = []
                for i in range(len(properties)):
                    prop = properties[i]
                    if (hasattr(resource, prop[PROP_METHOD])):
                        x = getattr(resource, prop[PROP_METHOD])
                        known[prop] = x()
                        x = None
                    else:
                        unknown.append(prop)
                # FOUND PROPERTIES
                if (len(known) > 0):
                    with response.container('D:propstat'):
                        response.element('D:status', text='HTTP/1.1 200 OK')
                        with response.container('D:prop'):
                            for prop in known.keys():
                                if (known[prop] is None):
                                    response.element(prop[PROP_PREFIXED])
                                else:
                                    # TODO: Can be handle non-string types more intelligently?
                                    response.file.write('<{0}>{1}</{0}>'.format(prop[PROP_PREFIXED], known[prop]))
                 # UNKNOWN PROPERTIES
                if (len(unknown) > 0):
                    with response.container('D:propstat'):
                        response.element('D:status', text='HTTP/1.1 404 Not found')
                        with response.container('D:prop'):
                            for prop in unknown:
                                response.element(prop[PROP_PREFIXED])
