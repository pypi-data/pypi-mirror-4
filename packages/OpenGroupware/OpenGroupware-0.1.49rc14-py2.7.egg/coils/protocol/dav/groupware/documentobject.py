# Copyright (c) 2010 Tauno Williams <awilliam@whitemice.org>
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
import urllib
from StringIO             import StringIO
from time                 import strftime, gmtime, time
from coils.core           import *
from coils.net            import DAVObject, Parser
from coils.net.ossf       import MarshallOSSFChain
from coils.foundation.api       import elementflow

class DocumentObject(DAVObject):
    _MIME_MAP_ = None

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        if (DocumentObject._MIME_MAP_ is None):
            sd = ServerDefaultsManager()
            self._mime_type_map = sd.default_as_dict('CoilsExtensionMIMEMap')

    def __repr__(self):
        return '<DocumentObject path="{0}"/>'.format(self.get_path())

    #
    # General WebDAV properies
    #

    def get_property_webdav_getlastmodified(self):
        x = gmtime(time())
        return strftime("%a, %d %b %Y %H:%M:%S GMT", x)

    def get_property_webdav_getcontentlength(self):
        return str(self.entity.file_size)

    def get_property_webdav_creationdate(self):
        if (self.entity.created is not None):
            return self.entity.created.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            return self.get_property_webdav_getlastmodified()

    def get_property_webdav_getlastmodified(self):
        if (self.entity.modified is not None):
            return self.entity.modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime(time()))

    def get_property_webdav_getcontenttype(self):
        return self.entity.get_mimetype(type_map=self._mime_type_map)

    #
    # M$ WebDAV support
    #

    def get_mswebdav_property(self, name, default = None):
        prop = self.context.property_manager.get_property(self.entity,
                                                          'http://www.opengroupware.us/mswebdav',
                                                          'win32fileattributes')
        if prop is None:
            return default
        return prop.get_value()

    def set_mswebdav_property(self, name, value):
        self.context.property_manager.set_property(self.entity,
                                                   'http://www.opengroupware.us/mswebdav',
                                                   name,
                                                   value)

    # win32fileattributes

    def get_property_mswebdav_win32fileattributes(self):
        return self.get_mswebdav_property('win32fileattributes', '00000020')

    def set_property_mswebdav_win32fileattributes(self, value):
        # TODO: Can we verify this value in any way?
        return self.set_mswebdav_property('win32fileattributes', value)

    # win32lastmodifiedtime
    def get_property_mswebdav_win32lastmodifiedtime(self):
        return self.get_mswebdav_property('win32lastmodifiedtime', self.get_property_webdav_getlastmodified())

    def set_property_mswebdav_win32lastmodifiedtime(self, value):
        # TODO: Should we also update the entitie's last modified time stamp?
        return self.set_mswebdav_property('win32lastmodifiedtime', value)

    # win32lastaccesstime
    def get_property_mswebdav_win32lastaccesstime(self):
        # TODO: Can we retrieve a better time from the log? That would be a good default
        return self.get_mswebdav_property('win32lastaccesstime', None)

    def set_property_mswebdav_win32lastaccesstime(self, value):
        return self.set_mswebdav_property('win32lastaccesstime', value)

    # win32creationtime
    def get_property_mswebdav_win32creationtime(self):
        # TODO: Doesn't the entity itself already know this? That would be a good default.
        return self.get_mswebdav_property('win32creationtime', None)

    def set_property_mswebdav_win32creationtime(self, value):
        return self.set_mswebdav_property('win32creationtime', value)

    #
    # Coils Custom Properties
    #

    def get_property_coils_checksum(self):
        return self.entity.checksum
                
    def get_property_coils_ownerid(self):
        return unicode(self.entity.owner_id)
                
    def get_property_coils_revisioncount(self):
        return unicode(self.entity.version_count)

    #
    # Method Handlers
    #

    def do_HEAD(self):
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=self.entity.get_mimetype(type_map=self._mime_type_map),
                                     headers={ 'etag': self.get_property_getetag(),
                                               'Content-Length': str(self.entity.file_size) } )

    def do_GET(self):
        handle = self.context.run_command('document::get-handle', id=self.entity.object_id)
        self.log.debug('Document MIME-Type is "{0}"'.format(self.entity.mimetype))
        handle, mimetype = MarshallOSSFChain(handle, self.entity.mimetype, self.parameters)
        self.log.debug('MIME-Type after OSSF processing is {0}'.format(mimetype))
        self.context.run_command('document::record-download', document=self.entity)
        self.context.commit()
        self.request.stream_response(200,
                                     stream=handle,
                                     mimetype=mimetype,
                                     headers={ 'etag': self.get_property_getetag() } )
        BLOBManager.Close(handle)
