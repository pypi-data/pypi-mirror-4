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
import logging
from xml.dom    import minidom
from coils.core import NotImplementedException
from parser     import Parser
from namespaces import XML_NAMESPACE, ALL_PROPS

PROP_METHOD    = 0
PROP_NAMESPACE = 1
PROP_LOCALNAME = 2
PROP_DOMAIN    = 3

class Report(object):

    def __init__(self, document, user_agent_description):
        self._source  = document
        self._properties   = None  # Properties
        self._namespaces   = None
        self._params       = None  # Parameters
        self._hrefs        = None  # References
        self._uad          = user_agent_description

    @property
    def properties(self):
        if (self._properties is None):
            """
            properties = [ ]
            if document.getElementsByTagNameNS("DAV:", "allprop"):
                return Parser._all_props()
            else:
                for node in document.getElementsByTagNameNS("DAV:", "prop"):
                    for element in node.childNodes:
                        if element.nodeType == minidom.Node.ELEMENT_NODE:
                            namespace = element.namespaceURI
                            propname  = element.localName
                            properties.append((Parser.property_method_name(namespace, propname),
                                               namespace,
                                               propname,
                                               Parser.domain_from_namespace(namespace)))"""
            self._properties, self._namespaces = Parser.properties(self._source, self._uad)
            if (len(self._properties) == 0):
                properties = ALL_PROPS
        return self._properties, self._namespaces

    @property
    def report_name(self):
        raise NotImplementedException('This report is unnamed.')

    @property
    def parameters(self):
        raise NotImplementedException('This report does not implement parameter parsing.')

    @property
    def command(self):
        raise NotImplementedException('This report does not specify a Logic command.')

    @property
    def references(self):
        raise NotImplementedException('This report does not enumerate references.')
