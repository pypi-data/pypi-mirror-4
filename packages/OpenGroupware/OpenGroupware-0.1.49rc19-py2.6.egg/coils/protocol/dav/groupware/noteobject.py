#
# Copyright (c) 2010, 2011, 2012
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
import os
from xml.sax.saxutils                  import escape
from coils.core                        import BLOBManager
from coils.net                         import DAVObject
from groupwareobject                   import GroupwareObject

class NoteObject(DAVObject, GroupwareObject):
    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_webdav_getcontenttype(self):
        if self.context.user_agent_description[ 'webdav' ][ 'supportsMEMOs' ]:
            return 'calendar/ics'
        else:
            return 'text/plain'

    def get_property_caldav_calendar_data(self):
        return escape(self.get_representation())

    def get_property_webdav_getcontentlength(self):
        # Notes are funny things.  For clients that support VJOURNAL iCalendar objects we present them
        # as VJOURNAL objects, but VJOURNAL objects are sadly under supported.  In other cases we just
        # present them as text files.  So notes have two different "file" sizes depending upon the
        # user agent.

        dentry = self.dir_entry

        # First try to get file size from ObjectInfo
        if dentry:
            if self.context.user_agent_description[ 'webdav' ][ 'supportsMEMOs' ] and dentry.ics_size:
                return dentry.ics_size
            elif dentry.file_size:
                return dentry.file_size

        # Deterimine the size lacking a dentry
        if self.context.user_agent_description[ 'webdav' ][ 'supportsMEMOs' ]:
            payload = self.get_representation( )
            if payload:
                return unicode( len( payload ) )
        elif self.entity:
            handle = self.context.run_command( 'note::get-handle', id=self.entity.object_id )
            handle.seek( 0, os.SEEK_END )
            size = handle.tell( )
            BLOBManager.Close( handle )
            return size

        # We give up, return 0
        # TODO: Generate an administrative notice
        return '0'

    def get_property_webdav_owner(self):
        return u'<D:href>{0}</D:href>'.\
            format(self.get_appropriate_href( '/dav/Contacts/{0}.vcf'.format( self.entity.owner_id ) ) )

    def do_GET(self):
        if self.context.user_agent_description[ 'webdav' ][ 'supportsMEMOs' ]:
            DAVObject.do_GET(self)
        else:
            handle = self.context.run_command( 'note::get-handle', id=self.entity.object_id )
            self.request.stream_response( 200,
                                          stream=handle,
                                          mimetype=self.entity.get_mimetype(),
                                          headers={ 'etag': self.get_property_webdav_getetag( ) } )
