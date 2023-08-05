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
from coils.net              import *
# DAV content providers
from groupware              import ContactsFolder, CalendarFolder, AccountsFolder, \
                                    TeamsFolder, TasksFolder, FavoritesFolder, \
                                    ProjectsFolder, CabinetsFolder, CollectionsFolder
from files                  import FilesFolder
from workflow               import WorkflowFolder

DAV_ROOT_FOLDERS = { 'Contacts'     : 'ContactsFolder',
                     'Projects'     : 'ProjectsFolder',
                     'Calendar'     : 'CalendarFolder',
                     'Journal'      : 'EmptyFolder',
                     'Collections'  : 'CollectionsFolder',
                     'Files'        : 'FilesFolder',
                     'Cabinets'     : 'CabinetsFolder',
                     'Users'        : 'AccountsFolder',
                     'Tasks'        : 'TasksFolder',
                     'Teams'        : 'TeamsFolder',
                     'Favorites'    : 'FavoritesFolder',
                     'Workflow'     : 'WorkflowFolder' }

class DAVRoot(DAVFolder, Protocol):
    '''The root of the DAV hierarchy.'''
    __pattern__   = [ 'dav', 'DAV' ]
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        DAVFolder.__init__(self, parent, 'dav', **params)
        DAVFolder.Root = self
        self.root = self

    def get_name(self):
        return 'dav'

    def _load_contents(self):
        self.init_context()
        for key in DAV_ROOT_FOLDERS.keys():
            classname = DAV_ROOT_FOLDERS[key]
            classclass = eval(classname)
            self.insert_child(key,
                              classclass(self, key, parameters=self.parameters,
                                                    request=self.request,
                                                    context=self.context))
        return True

    def get_property_webdav_current_user_principal(self):
        # RFC5397: WebDAV Current Principal Extension
        url = self.get_appropriate_href('/dav/Contacts/{0}.vcf'.format(self.context.account_id))
        return u'<D:href>{0}</D:href>'.format(url)


    def get_property_caldav_calendar_home_set(self):
        # RFC4791 : 
        # urls = [ self.request.user_agent.get_appropriate_href('/dav/Calendar/Overview'),
        #          self.request.user_agent.get_appropriate_href('/dav/Calendar/Personal') ]
        # return u''.join([  '<D:href>{0}</D:href>'.format(url) for url in urls ])
        url =  self.get_appropriate_href('/dav/Calendar')
        return '<D:href>{0}</D:href>'.format(url)


    def get_property_caldav_calendar_user_address_set(self):
        # RFC4791 : 9.2.3
        if isinstance(self.context, AuthenticatedContext):
            tmp = [ self.context.account_object.get_company_value('email1'),
                    self.context.account_object.get_company_value('email2'),
                    self.context.account_object.get_company_value('email3'), ]
            tmp = [ x.string_value for x in tmp if x ]
            tmp = [ '<D:href>mailto:{0}</D:href>'.format(x.strip()) for x in tmp if x ]
            return ''.join(tmp)
        return None
