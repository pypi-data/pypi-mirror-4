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
from xml.sax.saxutils import escape
from time import strftime, gmtime, time
# Core
from coils.foundation   import *
from coils.core         import *
# DAV Classses
from bufferedwriter     import BufferedWriter
from dav                import DAV
from reports            import Parser

from entity_map         import ENTITYMAP

class DAVObject(DAV):
    """ Represents an OpenGroupware entity in a DAV collection,  a GET will return the
        representation of the object - vCard, vEvent, vToDo, etc... """

    # The self.data in a DAVObject  to be a first-class ORM entity
    def __init__(self, parent, name, **params):
        #self.location = None
        DAV.__init__(self, parent, name, **params)
        self._representation = None

    #
    # Core
    #

    @property
    def is_object(self):
        return True

    #
    # Properties
    #

    def supports_GET(self):
        '''
        Enable GET operations, this is an object.
        '''
        return True

    def get_property_getetag(self):
        '''
        Generate the getetag value for the DAV representation of the object.
        This consists of object_id/uuid:version.  If the entity has neither
        a UUID or object_id identifier a 404 exception is raised in which case
        the property should be reported to the client as not-found. If the
        entity has no version attribute or the value of the version attribute
        is NULL the version value will be '0'.
        The value of getetag is described in RFC4918 15.6
        <http://www.webdav.org/specs/rfc4918.html#PROPERTY_getetag>
        '''
        if self.load_contents():
            if hasattr( self.entity, 'object_id' ):
                left = str( self.entity.object_id )
            elif hasattr(self.entity, 'uuid' ):
                left = self.entity.uuid.strip( )
            else:
                raise NoSuchPathException( 'No candidate property to generate etag value' )
        if hasattr( self.entity, 'version' ):
            if self.entity.version is None:
                return '{0}:0'.format( left, self.entity.version )
            else:
                return '{0}:{1}'.format( left, self.entity.version )
        else:
            return '{0}:0'.format( left )

    def get_property_unknown_getetag(self):
        '''
        If the client is using a confused namespace an asks for the getetag property
        we return the WebDAV getetag and just assume that is what they are talking
        about.
        '''
        return self.get_property_getetag()

    def get_property_webdav_getetag(self):
        '''
        Maps the getetag value to the WebDAV namespace attribute getetag
        '''
        return self.get_property_getetag()

    # PROP: ISCOLLECTION

    def get_property_unknown_iscollection(self):
        '''
        Map any request for iscollection from an unrecogninzed namespace to
        the WebDAV:iscollection non-standard property.  Clients using this
        attribute already demonstrate they have no idea what they are doing.
        '''
        return self.get_property_webdav_iscollection()

    def get_property_webdav_iscollection(self):
        '''
        This is a non-standard attribute very frequently used in the WebDAV
        namespace by a variety of broken clients [including M$-Windows] to
        determine if a resource is a collection or an object.
        <http://greenbytes.de/tech/webdav/draft-hopmann-collection-props-00.txt>
        '''
        return '0'

    # PROP: DISPLAYNAME

    def get_property_webdav_displayname(self):
        '''
        Defined in RFC2518 section 13.2.   The displayname property should be
        defined on all DAV compliant resources.  If present, the property
        contains a description of the resource that is suitable for presentation
        to a user.  Should the client be free to localize this response?  Nobody
        knows, that isn't documented, but it doesn't appear that many attempt to.
        '''
        return escape( self.name )

    # PROP: RESOURCETYPE

    def get_property_unknown_resourcetype(self):
        return self.get_property_webdav_resourcetype(self)

    def get_property_webdav_resourcetype(self):
        '''
        Defined in RFC2518 section 13.9. The resourcetype property MUST be defined
        on all DAV compliant resources.  The default value is empty.
        '''
        return ''

    # PROP: SOURCE

    def get_property_webdav_source(self):
        '''
        Defined in RFC2518 section 13.10. The destination of the source link
        identifies the resource that contains the unprocessed source of the
        link's source.  Description: The source of the link (src) is typically
        the URI of the output resource on which the link is defined, and there
        is typically only one destination (dst) of the link, which is the URI
        where the unprocessed source of the resource may be accessed.  When
        more than one link destination exists, this specification asserts no
        policy on ordering.
        Example: <D:src>http://foo.bar/program</D:src>
        '''
        raise NoSuchPathException( 'SOURCE property not implemented on this object.' )

    # PROP: GETCONTENTLENGTH

    def get_property_unknown_getcontentlength(self):
        '''
        Map getcontentlength in an unknown namespace to the WebDAV:getcontentlength.
        '''
        return self.get_property_webdav_getcontentlength()

    def get_property_webdav_getcontentlength(self):
        '''
        Defined in RFC2518 section 13.4. Contains the Content-Length header
        returned by a GET without accept headers. The getcontentlength
        property MUST be defined on any DAV compliant resource that returns
        the Content-Length header in response to a GET.
        '''
        # First try to get file size from ObjectInfo
        if self.dir_entry:
            if self.entity.info.ics_size:
                return self.entity.info.ics_size
        # Generate the representation and return the size
        payload = self.get_representation()
        if payload:
            return str(len(payload))
        return '0'

    # PROP: GETCONTENTTYPE

    def get_property_unknown_getcontenttype(self):
        '''
        Map the getcontenttype property from an unknown namespace to the
        WebDAV getcontenttype property.
        '''
        return get_property_webdav_getcontenttype(self)

    def get_property_webdav_getcontenttype(self):
        '''
        Defined in RFC2518 section 13.5. Contains the Content-Type header r
        eturned by a GET without accept headers. This getcontenttype property
        MUST be defined on any DAV compliant resource that returns the
        Content-Type header in response to a GET.
        '''
        if hasattr( self.entity, '__entityName__' ):
            if self.entity.__entityName__ in ENTITYMAP:
                return ENTITYMAP[ self.entity.__entityName__ ][ 'mime-type' ]
        return 'application/octet-stream'

    # PROP: HREF

    def get_property_unknown_href(self):
        return self.get_property_webdav_href()

    def get_property_webdav_href(self):
        return self.webdav_url

    #
    # Locking
    #

    def supports_LOCK(self):
        '''
        If this entity represents a proper entity then locking should work,
        so report that to the HTTP service provider.
        '''
        if hasattr( self, 'entity' ):
            if hasattr( self.entity, 'object_id' ):
                return True
        return False

    #
    # DATA LOAD
    #
    def get_keys(self):
        return None

    def _load_contents(self):
        if (self.entity is None):
            if (self.name.isdigit()):
                object_id = int(self.name)
                kind = self.context.type_manager.get_type(object_id)
                if (kind == 'Unknown'):
                    return False
                self.entity = self.context.run_command(ENTITYMAP[kind]['get-command'], id=object_id)
                if (self.entity is None):
                    return False
            else:
                return False
        return True

    def get_representation(self):
        if (self.load_contents()):
            command = ENTITYMAP[self.entity.__entityName__]['data-command']
            self.log.debug('Selected {0} to retrieve object representation.'.format(command))
            x = self.context.run_command(ENTITYMAP[self.entity.__entityName__]['data-command'],
                                         object=self.entity)
            if (x is None):
                self.log.warn('Data command for object representation returned None!')
                return ''
        return x

    def do_GET(self):
        if ((hasattr(self, 'location')) and (self.location is not None)):
            if (self.current_path != self.location):
                if self.context.user_agent_description['webdav']['supports301']:
                    self.log.debug('Redirecting client from {0} to {1}'.format(self.current_path, self.location))
                    self.request.simple_response(301, headers={ 'Location': self.location } )
                    return
                else:
                    self.log.warn('Redirectable request for "{0}" from user-agent "{1}" known to not ' \
                                  'support 301 responses; would have redirected to "{2}"'.\
                                  format(self.current_path,
                                         self.context.user_agent_description['name'],
                                         self.location))

        #check etag, maybe we can do a 304 response?
        etag_c = self.request.headers.get( 'If-None-Match', None )
        etag_s = self.get_property_getetag( )
        if etag_c:
            if etag_c == etag_s:
                self.request.simple_response(304,
                                     data=None,
                                     mimetype=ENTITYMAP[self.entity.__entityName__]['mime-type'],
                                     headers={ 'etag':  etag_s, } )

        payload = self.get_representation()
        if payload:
            self.request.simple_response(200,
                                         data=payload,
                                         mimetype=ENTITYMAP[self.entity.__entityName__]['mime-type'],
                                         headers={ 'Cache-Control': 'max-age=60480',
                                                   'ETag': etag_s, } )
            if self.context.is_dirty:
                self.context.commit()
            return
        else:
            raise NoSuchPathException('%s not found' % self.name)

    def do_HEAD(self):
        if ((hasattr(self, 'location')) and (self.location is not None)):
            if (self.current_path != self.location):
                if self.context.user_agent_description['webdav']['supports301']:
                    self.log.debug('Redirecting client from {0} to {1}'.format(self.current_path, self.location))
                    self.request.simple_response(301, headers={ 'Location': self.location } )
                    return
                else:
                    self.log.warn('Redirectable request for "{0}" from user-agent "{1}" known to not ' \
                                  'support 301 responses; would have redirected to "{2}"'.\
                                  format(self.current_path,
                                         self.context.user_agent_description['name'],
                                         self.location))
        x = self.get_representation()
        if (x is not None):
            # TODO: Will len(unicode(x)) actually give us the length of the payload in bytes?
            x = unicode(x)
            self.request.simple_response(204,
                                         data=None,
                                         mimetype=ENTITYMAP[self.entity.__entityName__]['mime-type'],
                                         headers={ 'ETag': self.get_property_getetag(),
                                                   'Content-Length': len(x) } )
            return
        else:
            raise NoSuchPathException('{0} not found'.format(self.name))
