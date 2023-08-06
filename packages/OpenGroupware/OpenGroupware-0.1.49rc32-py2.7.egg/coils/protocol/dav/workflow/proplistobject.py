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
from base64                             import b64encode
from StringIO                           import StringIO
from datetime                           import datetime
from coils.core                         import *
from coils.net                          import *

class PropertyListObject(DAVObject):
    ''' Represent a BPML markup object in WebDAV '''

    def __init__(self, parent, name, **params):
        self.version = None
        DAVObject.__init__(self, parent, name, **params)
        self.text = None

    def get_property_webdav_getetag(self):
        #TODO: Make this a proper etag, it must change on change
        return u'{0}:{1}:propertyList'.format(self.entity.object_id, self.entity.version)

    def get_property_webdav_displayname(self):
        return 'Object Property List'

    def get_property_webdav_getcontentlength(self):
        self.generate_property_list_text()
        return str(len(self.text))

    def get_property_webdav_getcontenttype(self):
        return 'text/plain'

    def get_property_webdav_creationdate(self):
        # Issue#164 - Implement PropertyListObject creation-date
        return datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def get_property_webdav_getlastmodified(self):
        # Issue#165 - Implement PropertyListObject modification-date
        return datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

    def generate_property_list_text(self):
        if self.text is None:
            props = self.context.property_manager.get_properties(self.entity)
            stream = StringIO(u'')
            if (len(props) > 0):
                for prop in props:
                    stream.write(u'{{{0}}}{1}\r\n'.format(prop.namespace, prop.name))
                    try:
                        x = None
                        x = unicode(prop.get_value())
                    except:
                        x = b64encode(prop.get_value)
                    finally:
                        stream.write(x)
                    stream.write(u'\r\n') # The newline following the property value
                    stream.write(u'\r\n') # The blank newline separating properties
            else:
                # No properties exist on the object; include a blank line
                stream.write(u'\r\n')
            self.text = stream.getvalue()
            stream.close()

    def do_GET(self):
        ''' Handle a GET request. '''
        self.generate_property_list_text()
        self.request.simple_response(200,
                                     data=self.text,
                                     mimetype='application/text',
                                     headers={ 'ETag': self.get_property_webdav_getetag() } )
