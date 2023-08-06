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
import io
from datetime                          import datetime
# Core
from coils.core                        import *
# DAV Classses
from coils.net                         import DAVObject

'''
    NOTES: 2010-08-09 Implemented WebDAV "principal-url" property RFC2744 (Access Control)
           2010-08-10 Implemented WebDAV "group-member-set" property RFC2744 (Access Control)
           2010-08-09 Implemented WebDAV "group" property RFC2744 (Access Control)
           2010-08-09 Implemented WebDAV "owner" property RFC2744 (Access Control)
            * Teams have no group and are owned by the Administrator [uid=10000]
'''

class TeamObject(DAVObject):
    
    def get_property_webdav_principal_url(self):
        return u'<href>/dav/Teams/{0}.vcf</href>'.format(self.entity.object_id)

    def get_property_webdav_owner(self):
        return u'<href>{0}</href>'.\
            format(self.get_appropriate_href('/dav/Contacts/10000.vcf'))

    def get_property_webdav_group(self):
        # TODO: Return URL of Team Creators group
        return None

    def get_property_webdav_group_member_set(self):
        members = [ ]
        for member in self.entity.members:
            href = self.get_appropriate_href('/dav/Contacts/{0}.vcf'.format(member.child_id))
            members.append('<href>{0}</href>'.format(href))
        return u''.join(members)

    def get_representation(self):
        if (self._representation is None):
            self._representation = self.context.run_command('object::get-as-ics', object=self.entity)
        return self._representation
