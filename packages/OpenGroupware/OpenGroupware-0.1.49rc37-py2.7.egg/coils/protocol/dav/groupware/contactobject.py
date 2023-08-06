#!/usr/bin/env python
# Copyright (c) 2009, 2011, 2012, 2013
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
from coils.net        import DAVObject
from groupwareobject  import GroupwareObject

'''
NOTE: 2010-09-14 Implemented WebDAV "owner" property RFC2744 (Access Control)
                 Implemented WebDAV "group-membership" property RFC2744 (Access Control)
                 Implemented WebDAV "group" property RFC2744 (Access Control)

TODO: DAV:current-user-privilege-set
      DAV:acl
      DAV:acl-restrictions
      CALDAV:calendar-home-set Issue#114
'''

class ContactObject(DAVObject, GroupwareObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def get_property_webdav_principal_url(self):
        return u'<D:href>{0}</D:href>'.\
            format(self.get_appropriate_href( '/dav/Contacts/{0}'.format( self.entity.get_file_name( ) ) ) )


    def get_property_webdav_owner(self):
        owner_id = self.entity.owner_id if self.entity.owner_id else 10000
        return u'<D:href>{0}</D:href>'.\
            format(self.get_appropriate_href( '/dav/Contacts/{0}.vcf'.format( owner_id ) ) )

    def get_property_webdav_group(self):
        return None

    def get_property_webdav_group_membership(self):
        if self.entity.is_account:
            teams = self.context.run_command('team::get', member_id=self.entity.object_id)
            groups = [ ]
            for team in teams:
                url = self.get_appropriate_href('/dav/Teams/{0}.vcf'.format(team.object_id))
                groups.append('<D:href>{0}</D:href>'.format(url))
            return u''.join(groups)
        else:
            return None

    def get_property_caldav_calendar_home_set(self):
        if self.entity.is_account:
            if self.entity.object_id == self.context.account_id:
                return u'<D:href>/dav/Calendar/</D:href>'
        self.no_such_path( )

    def get_property_caldav_calendar_user_address_set(self):
        result = [ ]
        for cv_name in [ 'email1', 'email2', 'email3' ]:
            cv = self.entity.company_values.get( cv_name, None )
            if cv:
                if cv.string_value:
                    result.append( '<D:href>{0}</D:href>'.format( cv.string_value ) )
        if result:
            return ''.join( result )
        return None

    def get_property_caldav_schedule_inbox_url(self):
        if self.entity.is_account:
            if self.entity.object_id == self.context.account_id:
                return u'<D:href>/dav/Calendar/Personal/</D:href>'
        self.no_such_path( )

    def get_property_caldav_schedule_outbox_url(self):
        if self.entity.is_account:
            if self.entity.object_id == self.context.account_id:
                return u'<D:href>/dav/Calendar/</D:href>'
        self.no_such_path( )

    def get_property_carddav_addressbook_home_set(self):
        if self.entity.is_account:
            if self.entity.object_id == self.context.account_id:
                return u'<D:href>/dav/Contacts/</D:href>'
        self.no_such_path( )

    def get_property_carddav_address_data(self):
        return escape( self.get_representation( ) )

    def get_property_icewarp_default_contacts_url(self):
        if self.entity.is_account:
            if self.entity.object_id == self.context.account_id:
                return u'<D:href>/dav/Contacts/Favorites/</D:href>'
        self.no_such_path( )

    def get_property_icewarp_default_tasks_url(self):
        if self.entity.is_account:
            if self.entity.object_id == self.context.account_id:
                return u'<D:href>/dav/Tasks/ToDo/</D:href>'
        self.no_such_path( )

    def get_property_icewarp_default_calendar_url(self):
        if self.entity.is_account:
            if self.entity.object_id == self.context.account_id:
                return u'<D:href>/dav/Calender/Personal/</D:href>'
        self.no_such_path( )

    def get_property_coils_first_name(self):
        return self.entity.first_name

    def get_property_coils_last_name(self):
        return self.entity.last_name

    def get_property_coils_file_as(self):
        return self.entity.file_as

    def get_property_coils_is_account(self):
        if (self.entity.is_account):
            return 'true'
        return 'false'

    def get_property_coils_gender(self):
        if (self.entity.gender is None):
            return 'unknown'
        return self.entity.gender.lower()

    def get_representation(self):
        if not self._representation:
            self._representation = self.context.run_command('object::get-as-ics', object=self.entity)
        return self._representation
