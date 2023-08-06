#
# Copyright (c) 2009, 2011, 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
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
import xmldict, urllib, json, re
from StringIO             import StringIO
from coils.core           import *
from pathobject           import PathObject
from bufferedwriter       import BufferedWriter
from reports              import Parser, REVERSE_XML_NAMESPACE, introspect_properties
from xml.sax.saxutils     import escape
from coils.foundation.api       import elementflow
from itertools import izip

PATH_CACHE = { }
USE_CACHE = False

PROP_METHOD    = 0
PROP_NAMESPACE = 1
PROP_LOCALNAME = 2
PROP_DOMAIN    = 3
PROP_PREFIXED  = 4

class DAV(PathObject):
    '''
    Base class used by DAVObject and DAVFolder.  This object provides basic property
    handling and some default methods.  This object assumes all operations are disabled
    so child objects MUST enabled the appropriate operations.
    '''

    def get_appropriate_href(self, href):
        server_name = self.request.headers.get( 'Host', self.request.server_name )
        server_port = self.request.headers.get( 'X-Real-Port', self.request.server_port )

        if self.context.user_agent_description[ 'webdav' ][ 'quoteDAVHref' ]:
            href = urllib.quote( href )

        if self.context.user_agent_description[ 'webdav' ][ 'absoluteHrefs' ]:
            ''' Absolute HREF  '''

            if self.request.headers.get( 'X-Is-HTTPS', None ):
                protocol = 'https'
            else:
                protocol = 'http'

            if PathObject.__discardPortOnAbsoluteURLs__:
                url = u'{0}://{1}{2}'.format( protocol, server_name, href )
            else:
                url = u'{0}://{1}:{2}{3}'.format( protocol, server_name, server_port, href )
        else:
            ''' Relative HREF '''
            url = href

        if self.is_folder:
            # TODO: What about parameter string?
            if not url.endswith( '/' ):
                url += '/'

        return url


    def __init__(self, parent, name, **params):
        ''' Root DAV Object;  provides utility methods for implementing WebDAV.

        Keyword Arguments:
        parent - The parent object in the DAV hierarchy, should be a DAV object
        name - The name of this object, as used in the URL

        Additional named parameters are used to directly set attributes of this
        object,  so you you set fred=123 an attribute of fred will be set on the
        object with a value of 123.
        '''
        self.name = name
        self._dentry = None
        self._contents = None
        self._aliases  = None
        self._depth    = -1
        PathObject.__init__(self, parent, **params)
        if hasattr(parent, 'root'):
            self._root = parent.root
        else:
            self._root = None
        if (not hasattr(PathObject, '__discardPortOnAbsoluteURLs__')):
            sd = ServerDefaultsManager()
            PathObject.__discardPortOnAbsoluteURLs__ = sd.bool_for_default('DAVDiscardServerPort')
            server_name = sd.string_for_default('DAVHostForHref')
            if (len(server_name)):
                PathObject.__davServerName__ = server_name
            else:
                PathObject.__davServerName__ = None

    #
    # Core
    #

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value

    @property
    def dir_entry(self):

        def lookup_dentry(self):
            if hasattr(self, 'entity'):
                if hasattr(self.entity, 'info'):
                    if self.entity.info:
                        if self.entity.info.version == self.entity.version:
                            return self.entity.info
                ObjectInfoManager.Repair(self.entity, self.context, log=self.log)
            return None

        if self._dentry is None:
            dentry = lookup_dentry(self)
            if dentry:
                self._dentry = dentry
            else:
                self._dentry = False

        if self._dentry:
            return self._dentry

        return None

    @property
    def is_folder(self):
        '''
        Return True if this object is folder/collection.
        '''
        return False

    @property
    def is_object(self):
        '''
        Return True if this object is a resource.
        '''
        return False

    def get_path(self):
        '''
        Reconstruct the path used to arrive at this object
        '''
        return self.current_path

    def get_parent_path(self):
        return self.parent.get_path()

    def quoted_value(self, value):
        if '&' in value or '<' in value or '"' in value:
            value = value.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')
        return value

    def unquoted_value(self, value):
        if '&amp;' in value or '&lt;' in value or '&quot;' in value:
            value = value.replace('&amp;', '&').replace('&lt;', '<').replace('&quot;', '"')
        return value

    @property
    def url(self):
        '''
        Returns the absolute HTTP path to this object.
        '''
        return self.get_absolute_path()

    @property
    def webdav_url(self):
        '''
        Returns the HTTP path this object mangled in such a way as to attempt
        to appease the flakiness of the client the user is afflicted with.
        '''
        return self.get_appropriate_href(self.current_path)

    @property
    def current_path(self):
        '''
        Returns the path used in the current request to arrive at this object
        '''
        path = self.name
        x = self.parent
        while (x is not None):
            path = '%s/%s' % (x.get_name(), path)
            x = x.parent
        return self.quoted_value(path)

    @property
    def current_url(self):
        return self.get_appropriate_href(self.current_path)

    #
    # Contents
    #
    def insert_child(self, key, value, alias=None):
        key = unicode(key)
        if (self._contents is None): self._contents = { }
        if (self._aliases is None): self._aliases = { }
        self._contents[unicode(key)] = value
        if (alias is not None):
            self._aliases[unicode(alias)] = key
        else:
            self._aliases[unicode(key)] = key

    def empty_content(self):
        if (self._contents is None): self._contents = { }
        if (self._aliases is None): self._aliases = { }

    def get_alias_for_key(self, key):
        if (self._aliases is None):
            return key
        name = self._aliases.get(unicode(key), key)
        return name

    def get_child(self, key, minimum_components = 1,
                             component_seperator='.',
                             supports_aliases=True):
        result = None
        # We always process keys as strings
        key = str(key)
        if (self._aliases is None): self.log.error('Aliases is not initialized')
        if (self._contents is None): self.log.error('Contents is not initialized')
        if (supports_aliases):
            # If aliases are enabled and the key matches then the key is replaced by the
            # value from the _aliases dict
            if (key in self._aliases):
                key = self._aliases[key]
        key = key.split(component_seperator)
        for i in range(len(key), 0 , -1):
            if (i < minimum_components): break
            result = self._contents.get(u'.'.join(key[0:i]), None)
            if (result is not None):
                break;
        return result

    def has_child(self, key, minimum_components = 1,
                             component_seperator='.',
                             supports_aliases=True):
        if (self.get_child(key, minimum_components=minimum_components,
                                component_seperator=component_seperator,
                                supports_aliases=supports_aliases) is None):
            return False
        return True

    def get_children(self):
        return self._contents.values()

    def no_such_path(self):
        raise NoSuchPathException( 'Not such path as {0}'.format( self.request.path ) )

    @property
    def is_loaded(self):
        if (self._contents is None):
            return False
        return True

    def load_contents(self):
        ''' If the DAV objects does not contain any data (self.data is None) then
            an attempt is made to retrieve the relevent information.  This method
            calls the _load_self() which the child is expected to implement. '''
        if (self.is_loaded):
            return True
        if (self._load_contents()):
            if (self._contents is None): self._contents = {}
            if (self._aliases is None): self._aliases = {}
            return True
        return False

    def _load_contents(self):
        # NOTE: All children must implement this method
        return True

    def get_keys(self):
        if (self.load_contents()):
            return self._contents.keys()
        return [ ]

    def get_aliased_keys(self):
        if (self.load_contents()):
            return self._aliases.keys()
        return [ ]

    #
    # Properties
    #

    # PROP: HREF
    def get_property_webdav_href(self):
        return self.quoted_value(self.webdav_url)

    def get_ctag(self):
        ''' Return a ctag appropriate for this object.
            Actual WebDAV objects should override this method '''
        # Child should override, it knows how to compute or derive its ctag.
        return '0'

    # PROP: EXECUTABLE

    def get_property_webdav_executable(self):
        return self.get_property_apache_executable()

    def get_property_apache_executable(self):
        return '0'

    # PROP: CREATIONDATE

    def get_property_unknown_creationdate(self):
        return self.get_property_webdav_creationdate()

    def get_property_webdav_creationdate(self):

        if self.dir_entry:
            if self.dir_entry.created:
                return self.dir_entry.created.strftime("%a, %d %b %Y %H:%M:%S GMT")

        if (hasattr(self, 'entity')):
            if ((self.load_contents()) and hasattr(self.entity, 'created')):
                if (self.entity.created is not None):
                    return self.entity.created.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # Default value; we must provide some value for this property in all cases
        return 'Thu, 09 Sep 2010 10:17:06 GMT'

    # PROP: GETLASTMODIFIED

    def get_property_unknown_getlastmodified(self):
        return self.get_property_webdav_getlastmodified()

    def get_property_webdav_getlastmodified(self):

        if self.dir_entry:
            if self.dir_entry.modified:
                return self.dir_entry.modified.strftime("%a, %d %b %Y %H:%M:%S GMT")

        if (hasattr(self, 'entity')):
            #self.log.debug('DAV presentation object has entity attribute')
            if ((self.load_contents()) and hasattr(self.entity, 'modified')):
                if (self.entity.modified is not None):
                    #self.log.debug('DAV presentation object has modified time')
                    return self.entity.modified.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # Default value; we must provide some value for this property in all cases
        return 'Thu, 09 Sep 2010 10:17:06 GMT'

    def get_property_webdav_current_user_principal(self):
        # RFC5397: WebDAV Current Principal Extension
        pattern = self.context.user_agent_description['webdav']['principalURL']
        if pattern:
            url = pattern
        else:
            url = '/dav/Users/{0}.vcf'.format( self.context.account_id )
        return u'<D:href>{0}</D:href>'.format( url )

    # PROP: supportedlock

    def get_property_webdav_supportedlock(self):
        if self.supports_LOCK( ):
            return '<D:lockentry>' \
                     '<D:lockscope><D:exclusive/></D:lockscope>' \
                     '<D:locktype><D:write/></D:locktype>' \
                   '</D:lockentry>'
        else:
            return None


    # PROP: lockdiscovery

    def get_property_webdav_lockdiscovery(self):
        if self.supports_LOCK( ):
            # TODO: Implement
            ''' <D:activelock>
                  <D:locktype><D:write/></D:locktype>
                  <D:lockscope><D:exclusive/></D:lockscope>
                  <D:depth>infinity</D:depth>
                  <D:owner>...</D:owner>
                  <D:timeout>Second-3600</D:timeout>
                  <D:locktoken><D:href>opaquelocktoken:....</D:href></D:locktoken>
                </D:activelock>'''
            return None
        else:
            return None

    # PROP: Coils revision
    def get_property_coils_revision(self):
        if hasattr(self, 'entity'):
            if hasattr(self.entity, 'version'):
                if self.entity.version:
                    return unicode(self.entity.version)
        return None

    # PROP: Coils objectId
    def get_property_coils_objectid(self):
        if hasattr(self, 'entity'):
            if hasattr(self.entity, 'object_id'):
                if self.entity.version:
                    return unicode(self.entity.object_id)
        return None

    #
    # OPTIONS Support
    #

    def supports_GET(self):
        return False

    def supports_POST(self):
        return False

    def supports_PUT(self):
        return False

    def supports_DELETE(self):
        return False

    def supports_PROPFIND(self):
        return True

    def supports_PROPPATCH(self):
        return True

    def supports_MKCOL(self):
        return False

    def supports_MOVE(self):
        return False

    def supports_LOCK(self):
        return False

    def supports_UNLOCK(self):
        # UNLOCK support is assumed if LOCK support is togged on
        return self.supports_LOCK()

    def supports_REPORT(self):
        return False

    def supports_ACL(self):
        return False

    def get_methods(self):
        return ['GET', 'POST', 'PUT', 'DELETE', 'PROPFIND', 'PROPPATCH', 'MKCOL',
                 'MOVE', 'UNLOCK', 'LOCK', 'REPORT', 'ACL']

    def supports_operation(self, operation):
        operation = operation.upper().strip()
        method = 'supports_{0}'.format(operation)
        if (hasattr(self, method)):
            return getattr(self, method)()
        return False

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'HEAD', 'OPTIONS' ]
        for method in self.get_methods():
            if (self.supports_operation(method)):
                methods.append(method)
        self.request.simple_response(200,
                                     data=None,
                                     headers={ 'DAV': '1',
                                               'Allow': ','.join(methods),
                                               'Connection': 'close',
                                               'MS-Author-Via': 'DAV'})

    #
    # PROPFIND support
    #

    def parse_propfind_for_property_names(self, payload):
        if not self.context:
            raise CoilsException('Operation has no context!')
        return Parser.propfind(payload, user_agent_description=self.context.user_agent_description)

    def do_PROPFIND(self):
        '''
        Respond to a PROPFIND request.
        RFC2518 Section 8.1
        The depth property of the request determines if this is an
        examination of the collection object (depth 0) or an
        examination of the collections contents (depth 1). If no
        depth is specified a depth of inifinity must be assumed
        [according to the spec; yes, that is stupid, but that is
        the spec].
        '''

        depth = Parser.get_depth(self.request)
        if (depth == '1'):
            depth = 2
        elif (depth == '0'):
            depth = 1
        else:
            # HACK: infinity = 25
            depth = 25

        payload = self.request.get_request_payload()
        props, namespaces = self.parse_propfind_for_property_names(payload)
        w = StringIO('')
        with elementflow.xml(w, u'D:multistatus', indent=True, namespaces=namespaces) as xml:
            if (isinstance(props, basestring)):
                if (props  == 'ALLPROP'):
                    self.do_property_propfind(depth=depth, response=xml, allprop=True)
                elif (props == 'PROPNAME'):
                    self.do_propname_propfind(depth=depth, response=xml)
                else:
                    raise CoilsException('Unimplemented special case from PROPFIND parser')
            elif (isinstance(props, list)):
                # Send PROPFIND response header
                self.do_property_propfind(props=props, depth=depth, response=xml)
            else:
                raise CoilsException('Unrecognzed response from PROPFIND parser')

        headers={'X-Dav-Error': '200 No error',
                 'Ms-Author-Via': 'DAV' }
        if hasattr(self, 'location'):
            if self.context.user_agent_description['webdav']['supports301']:
                headers['Location'] = self.location
        self.request.simple_response(207,
                                     data=w.getvalue(),
                                     mimetype='text/xml; charset="utf-8"',
                                     headers=headers)
        if self.context.is_dirty:
            self.context.commit()

    def do_propname_propfind(self, depth=25, response=None):
        self.do_propname_response(depth=depth, response=response)

    def do_propname_response(self, depth=25, response=None):
        # TODO: Re-Implement
        #raise NotImplementedException('PROPNAME PROPFIND needs to be reimplemnted')
        # Generate a propname response for "target" object, this method will
        # recurse until depth reaches -1
        abbreviations = {}
        properties, namespaces = introspect_properties(self)

        with response.container('D:response', namespaces=namespaces) as xml:
            xml.element('D:href', text=self.webdav_url)
            with xml.container('D:propstat'):
                for prop in properties:
                    xml.element(prop[4])
                xml.element('D:status', text='HTTP/1.1 200 OK')
        depth += -1
        if ((depth > 0) and (self.is_folder)):
            self.load_contents()
            for key in self.get_aliased_keys():
                result = self.get_object_for_key(key, auto_load_enabled=True, is_webdav=True)
                result.do_propname_response(depth=depth, response=response)

    def do_property_propfind(self, props=[], depth=25, response=None, allprop=False):
        self.do_property_response(props=props, depth=depth, response=response, allprop=allprop)

    def do_property_response(self, props=[], depth=25, response=None, allprop=False):
        known = {}
        unknown = []
        # In case of an allprop discover what properties this object has
        if (allprop):
            props, namespaces = introspect_properties(self)
        # discover property values and undefined properties
        for i in range(len(props)):
            prop = props[i]
            if hasattr( self, prop[ PROP_METHOD ] ):
                x = getattr( self, prop[ PROP_METHOD ] )
                try:
                    known[ prop ] = x( )
                except NoSuchPathException as e:
                    # A property can report itself as unknown by raising a NoSuchPathException
                    unknown.append( prop )
                x = None
            else:
                unknown.append( prop )
        if (allprop):
            self.do_property_partial_response(depth=depth,
                                              response=response,
                                              allprop=True,
                                              known=known,
                                              unknown=unknown,
                                              namespaces=namespaces)
        else:
            self.do_property_partial_response(props=props,
                                              depth=depth,
                                              response=response,
                                              known=known,
                                              unknown=unknown,
                                              namespaces=[])

    def do_property_partial_response(self, props=None,
                                           depth=25,
                                           response=None,
                                           allprop=False,
                                           known=None,
                                           unknown=None,
                                           namespaces=None):
        with response.container('D:response', namespaces=namespaces):
            response.file.write(u'<D:href>{0}</D:href>'.format(self.webdav_url))
            # render found properties
            if (len(known) > 0):
                with response.container('D:propstat'):
                    response.element('D:status', text='HTTP/1.1 200 OK')
                    with response.container('D:prop'):
                        for prop in known.keys():
                            if (known[prop] is None):
                                response.element(prop[PROP_PREFIXED])
                            else:
                                # TODO: Can be handle non-string types more intelligently?
                                response.element(prop[PROP_PREFIXED], text=unicode(known[prop]), escape=False)
            # UNKNOWN PROPERTIES
            if (len(unknown) > 0):
                with response.container('D:propstat'):
                    response.element('D:status', text='HTTP/1.1 404 Not found')
                    with response.container('D:prop'):
                        for prop in unknown:
                            response.element(prop[PROP_PREFIXED])
        depth += -1
        if ((depth > 0) and (self.is_folder)):
            self.load_contents( )
            for key in self.get_aliased_keys( ):
                try:
                    result = self.get_object_for_key( key, auto_load_enabled=True, is_webdav=True )
                    result.do_property_response( props=props, depth=depth, response=response, allprop=allprop )
                except NoSuchPathException, e:
                    self.log.debug( 'PROPFIND skipped properties for key "{0}" due to a NoSuchPathException'.format( key ) )

    #
    # PROPPATCH support
    #

    def do_PROPPATCH(self):
        # TODO: Support un-setting of properties, this method ignores those
        payload = self.request.get_request_payload()
        set_props, unset_props, namespaces = Parser.proppatch(payload)
        w = StringIO('')
        with elementflow.xml(w, u'D:multistatus', indent=True, namespaces=namespaces) as xml:
            with xml.container('D:response'):
                for prop in set_props:
                    if (hasattr(self, prop[0])):
                        x = getattr(self, prop[0])
                        z = x(prop[5])
                        self.log.debug('setting {0} property via {1} method'.format(prop[4], prop[0]))
                        with xml.container('D:propstat'):
                            xml.element('D:prop', text=unicode('<{0}/>'.format(prop[4])), escape=False)
                            xml.element('D:status', text=unicode('HTTP/1.1 200 OK'))
                    else:
                        # TODO: Can we differentiate more reasons why? 424 vs 409 vs. 403?
                        # TODO: Is 404 a meaningful PROPFIND failure code?  Our docs only mention 409 & 424
                        with xml.container('D:propstat'):
                            xml.element('D:prop', text=unicode('<{0}/>'.format(prop[4])), escape=False)
                            xml.element('D:status', text=unicode('HTTP/1.1 403 Forbidden'))
        data = w.getvalue()
        w.close()
        self.context.commit()
        self.log.debug('Committed PROPPATCH to {0}'.format(self.entity))
        self.request.simple_response(207, data=data, mimetype='text/xml; charset=UTF-8')

    #
    #   LOCK / UNLOCK support
    #

    '''
    Lock data is - Timeout   From header of request, either Second-{value} or "Infinite".  Multiple values
                             may be separated by commas in order of preferance. Servers may ignore the specified
                             timeout and apply their own.
                   Scope:    from lockscope property, either shared or exclusive
                   Owner:    Ugh, either a string or XML, this is gnarly
                   Locktpye: 'write'


    LOCK /dav/Projects/Application%20-%20BIE/Documents/logo.bmp HTTP/1.1
    translate: f
    Timeout: Second-3600
    Content-Type: text/xml; charset="utf-8"
    User-Agent: Microsoft-WebDAV-MiniRedir/6.0.6001
    Host: 172.16.54.1:8080
    Content-Length: 195
    Connection: Keep-Alive
    Cache-Control: no-cache
    Pragma: no-cache
    Authorization: Basic YWRhbTpmcmVkMTIz

    <?xml version="1.0" encoding="utf-8" ?>
    <D:lockinfo xmlns:D="DAV:">
        <D:lockscope>
            <D:exclusive/>
        </D:lockscope>
        <D:locktype>
            <D:write/>
        </D:locktype>
        <D:owner>
            <D:href>adam</D:href>
        </D:owner>
    </D:lockinfo>
    '''

    def do_LOCK(self):
        # WARN: TODO: Needs to be updated to the new lock_manager contract
        if (self.supports_LOCK()):
            duration = 3600
            # TODO: Take the duration of the lock from the Timeout header
            payload = self.request.get_request_payload()
            if (len(payload) > 0):
                #
                # Has payload - this is a new lock request
                #
                try:
                    lockinfo = Parser.lockinfo(payload,
                                               self.entity.object_id,
                                               self.context.account_id)
                except Exception, e:
                    self.log.error('Failed to parse LOCK request: {0}'.format(payload))
                    self.log.exception(e)
                    raise CoilsException('Failed to parse LOCK request')
                status, lockinfo = self.context.lock_manager.lock(entity=self.entity, duration=duration, data=( lockinfo[ 'owner' ], ) )
            else:
                #
                # Has no payload, this is a lock refresh operation
                #
                header = self.request.headers.get('If')
                self.log.info('Got if header of {0}'.format(header))
                token = re.findall('opaquelocktoken:[A-z0-9-]*', header)[0][16:]
                self.log.info('Lock token is "{0}"'.format(token))
                status, lockinfo = self.context.lock_manager.refresh(token, 5400)
            self.log.debug('Lock info for LOCK operation: {0}'.format(lockinfo))
            self.context.commit()
            #
            # Prepare response
            #
            if lockinfo is None:
                # TODO: Cannot commit lock operation!  Return error
                pass
            w = StringIO( '' )
            with elementflow.xml( w, u'D:prop', indent=True, namespaces={ 'D': 'DAV' } ) as xml:
                with xml.container( 'D:lockdiscovery' ):
                    with xml.container( 'D:activelock' ):
                        with xml.container( 'D:locktype' ):
                            xml.element( 'D:write' )
                        with xml.container( 'D:lockscope' ):
                            xml.element( 'D:exclusive' )
                        xml.element( 'D:depth', text='0' )
                        owner_info = lockinfo.data[ 0 ]
                        if 'TEXT' in owner_info:
                            xml.element( 'D:owner', text=owner_info[ 'TEXT' ] )
                        else:
                            xml.file.write( owner_info[ 'XML' ] )
                        xml.element( 'D:timeout', text='Second-{0}'.format( duration ) )
                        with xml.container( 'D:locktoken' ):
                            xml.element( 'D:href', text=lockinfo.token )
            data = w.getvalue( )
            w.close( )
            self.request.simple_response(200, data=data,
                                              mimetype='text/xml; charset=UTF-8',
                                              headers = { 'Lock-Token': 'opaquelocktoken:{0}'.format( lockinfo.token ) } )
        else:
            raise NotSupportedException( 'Lock on this object is not supported.' )

    def do_UNLOCK(self):
        '''
        Perform an HTTP UNLOCK operation.
        '''
        if self.supports_UNLOCK( ):
            token = self.request.headers.get( 'Lock-Token' )
            if not token:
                raise CoilsException(' No Lock-Token specified in UNLOCk request; WebDAV protocol violation' )
            # The token will be enclosed in carets: <token>
            token = token[1:-1]
            self.context.lock_manager.unlock( entity=self.entity, token=token )
            self.context.commit( )
            self.request.simple_response(204)
        else:
            raise NotSupportedException( 'Locks on this object not supported by server' )
