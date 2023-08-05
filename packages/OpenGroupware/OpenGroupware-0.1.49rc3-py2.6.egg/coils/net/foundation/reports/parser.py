#
# Copyright (c) 2009, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import re, time, uuid
from lxml                     import etree
from itertools                import izip
from xml.dom                  import minidom
from coils.core               import CoilsException
from namespaces               import XML_NAMESPACE, ALL_PROPS, REVERSE_XML_NAMESPACE
#from caldav_calendar_query    import caldav_calendar_query
#from caldav_calendar_multiget import caldav_calendar_multiget

"""
    ['name', 'parentname', 'href', 'ishidden', 'isreadonly',
     'getcontenttype', 'contentclass', 'getcontentlanguage',
     'creationdate', 'lastaccessed', 'getlastmodified',
     'getcontentlength', 'iscollection', 'isstructureddocument',
     'defaultdocument', 'displayname', 'isroot', 'resourcetype']

"""

class Parser(object):

    @staticmethod
    def get_depth(request):
        if 'Depth' in request.headers:
            return request.headers['Depth'].lower()
        else:
            return 'infinity'

    @staticmethod
    def _all_props():
        # TODO: Need namespace support
        return ALL_PROPS

    @staticmethod
    def domain_from_namespace(namespace):
        if (namespace is None):
            return 'unknown'
        return XML_NAMESPACE.get(namespace.lower(), 'unknown')

    @staticmethod
    def property_method_name(namespace, propname):
        return 'get_property_{0}_{1}'.format(Parser.domain_from_namespace(namespace),
                                              propname.lower().replace('-', '_'))

    @staticmethod
    def property_set_method_name(namespace, propname):
        return 'set_property_{0}_{1}'.format(Parser.domain_from_namespace(namespace),
                                             propname.lower().replace('-', '_'))

    @staticmethod
    def propfind(payload, user_agent_description=None):
        ''' Consumes a PROPFIND and returns a list of property sets. '''
        if (len(payload) == 0):
            # If the PROPFIND had an empty payload then this is a request for the 'default' properties.
            # This is not a "standard" / RFC thing, it is just what many clients so.  Specifically
            # Microsoft's MiniRedirector requires a precise response to an empty PROPFIND
            return Parser.default_properties(user_agent_description)
        # Assuming the payload is valid XML
        document = minidom.parseString(payload)
        return Parser.properties(document, user_agent_description)

    @staticmethod
    def determine_first_dynamic_ordinal(namespaces):
        nm_ordinal = 0
        for key in namespaces.values():
            if ord(key) > nm_ordinal:
                nm_ordinal = ord(key) + 1
        #print('Starting dynamic namespace allocation at: {0}'.format(chr(nm_ordinal)))
        return nm_ordinal


    @staticmethod
    def default_properties(user_agent_description):
        properties = [ ]
        namespaces = user_agent_description['webdav']['defaultNamespaces']
        namespaces = dict(izip(namespaces.itervalues(),namespaces.iterkeys()))
        nm_ordinal = Parser.determine_first_dynamic_ordinal(namespaces)
        for record in user_agent_description['webdav']['defaultPropeties']:
            propname = record[0]
            namespace = record[1]
            if namespace.upper() == 'DAV:':
                prefix = 'D'
            elif namespace in namespaces:
                prefix = namespaces[namespace]
            else:
                prefix = chr(nm_ordinal)
                namespaces[prefix] = prefix
                nm_ordinal += 1
            properties.append((Parser.property_method_name(namespace, propname),
                               namespace,
                               propname,
                               Parser.domain_from_namespace(namespace),
                               '{0}:{1}'.format(prefix, propname)))
        namespaces = dict(izip(namespaces.itervalues(), namespaces.iterkeys()))
        return properties, namespaces

    @staticmethod
    def proppatch(payload, user_agent_description=None):
        ''' Consumes a PROPATCH and returns a set of property changes '''
        if (len(payload) == 0):
            raise CoilsException('PROPATCH operation has no payload')
        nm_ordinal = 74
        namespaces = { 'http://apache.org/dav/props/':   'A',
                       'urn:ietf:params:xml:ns:caldav':  'C',
                       'DAV:':                           'D',
                       'urn:ietf:params:xml:ns:carddav': 'E',
                       'http://groupdav.org/':           'G' }
        document = minidom.parseString(payload)
        set_props   = [ ]
        unset_props = [ ]
        for node in document.getElementsByTagNameNS("DAV:", "set"):
            for node in document.getElementsByTagNameNS("DAV:", "prop"):
                for element in node.childNodes:
                    if element.nodeType == minidom.Node.ELEMENT_NODE:
                        namespace = element.namespaceURI
                        propname = element.localName
                        if (namespace.upper() == 'DAV:'):
                            prefix = 'D'
                        elif namespace in namespaces:
                            prefix = namespaces[namespace]
                        else:
                            prefix = chr(nm_ordinal)
                            namespaces[namespace] = prefix
                            nm_ordinal += 1
                        set_props.append((Parser.property_set_method_name(namespace, propname),
                                          namespace,
                                          propname,
                                          Parser.domain_from_namespace(namespace),
                                          '{0}:{1}'.format(prefix, propname),
                                          element.firstChild.data))
        # TODO: Return properties to un-set, this method ignores those
        keys = namespaces.iterkeys()
        values = namespaces.itervalues()
        return set_props, unset_props, dict(izip(values, keys))

    @staticmethod
    def properties(document, user_agent_description):
        ''' Return a list of the DAV:prop attributes from the provided document

            Each list entry is a set of
             - corresponding property member name for value retrieval
             - the original namespace of the property
             - the local name of the property
             - the domain of the propery (derived from namespace)
             - prefixed propertyname '''
        properties = [ ]
        namespaces = user_agent_description['webdav']['defaultNamespaces']
        namespaces = dict(izip(namespaces.itervalues(),namespaces.iterkeys()))
        '''{ 'http://apache.org/dav/props/':   'A',
                       'urn:ietf:params:xml:ns:caldav':  'C',
                       'DAV:':                           'D',
                       'urn:ietf:params:xml:ns:carddav': 'E',
                       'http://groupdav.org/':           'G',
                     }'''
        nm_ordinal = Parser.determine_first_dynamic_ordinal(namespaces)
        # TODO: if a request contains allprop, or propname, it must be solo!
        #        any combination of those to elements with each other or a
        #        prop element should raise an HTTP 400 Bad Request response
        if document.getElementsByTagNameNS("DAV:", "allprop"):
            properties = 'ALLPROP'
        elif document.getElementsByTagNameNS("DAV:", "propname"):
            properties = 'PROPNAME'
        else:
            for node in document.getElementsByTagNameNS("DAV:", "prop"):
                for element in node.childNodes:
                    if element.nodeType == minidom.Node.ELEMENT_NODE:
                        namespace = element.namespaceURI
                        if (namespace.upper() == 'DAV:'):
                            prefix = 'D'
                        elif namespace in namespaces:
                            prefix = namespaces[namespace]
                        else:
                            prefix = chr(nm_ordinal)
                            namespaces[namespace] = prefix
                            nm_ordinal += 1
                        propname  = element.localName
                        properties.append((Parser.property_method_name(namespace, propname),
                                           namespace,
                                           propname,
                                           Parser.domain_from_namespace(namespace),
                                           '{0}:{1}'.format(prefix, propname)))
        return properties, dict(izip(namespaces.itervalues(), namespaces.iterkeys()))

    @staticmethod
    def report(payload, user_agent_description):
        from caldav_calendar_query    import caldav_calendar_query
        from caldav_calendar_multiget import caldav_calendar_multiget
        document = minidom.parseString(payload)
        namespace = document.documentElement.namespaceURI
        if (namespace is None):
            domain = 'unknown'
        else:
            domain = XML_NAMESPACE.get(namespace.lower(), 'unknown')
        localname = document.documentElement.localName.lower().replace('-', '_')
        parserclassname = '{0}_{1}'.format(domain, localname)
        try:
            parserclass = eval(parserclassname)
            parser = parserclass(document, user_agent_description)
        except Exception, e:
            #TODO: Add a logger here!
            #self.log.exception(e)
            #self.log.warn('No parser class for REPORT {0} {1}'.format(namespace, localname))
            #self.log.debug(payload)
            raise CoilsException('No parser available for specified report')
        else:
            return parser

    @staticmethod
    def lockinfo(payload, object_id, context_id):
        lockinfo = { 'token':     str(uuid.uuid4()),
                     'objectId':  object_id,
                     'ownerId':   context_id,
                     'expires':   0,
                     'granted':   0,
                     'kind':      'W',
                     'owner':     { },
                     'exclusive': 'Y' }
        locktext = etree.fromstring(payload)
        if locktext.tag == '{DAV:}lockinfo':
            for child in list(locktext):
                if child.tag == '{DAV:}lockscope':
                    # TODO: this is fragile
                    children = child.getchildren()
                    if children[0].tag == '{DAV:}exclusive':
                        lockinfo['exclusive'] = 'Y'
                    else:
                        lockinfo['exclusive'] = 'N'
                elif child.tag == '{DAV:}locktype':
                    children = child.getchildren()
                    if children[0].tag == '{DAV:}write':
                        lockinfo['kind'] = 'W'
                    else:
                        lockinfo['kind'] = 'U'
                elif child.tag == '{DAV:}owner':
                    children = child.getchildren()
                    if len(children) == 0:
                        lockinfo['owner']['TEXT'] = child.text
                    else:
                        lockinfo['owner']['XML'] =  etree.tostring(child)
        return lockinfo