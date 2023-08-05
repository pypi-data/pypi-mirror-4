# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime                          import datetime
# DAV Classses
from coils.net     import DAVObject, DAVFolder
from groupwarefolder                   import GroupwareFolder

class AccountsFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    # PROP: GETCTAG

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    def get_ctag(self):
        return self.get_ctag_for_collection()

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, COPY, MOVE',
                    'PROPFIND, PROPPATCH, LOCK, UNLOCK, REPORT, ACL' ]
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=u'text/plain',
                                     headers={ 'DAV':           '1, 2, access-control, addressbook',
                                               'Allow':         ','.join(methods),
                                               'Connection':    'close',
                                               'MS-Author-Via': 'DAV'} )

    # CONTENTS (Implementation)

    def _load_contents(self):
        accounts = self.context.run_command('account::get-all')
        for account in accounts:
            if (account.carddav_uid is None):
                self.insert_child(account.object_id, account, alias='{0}.vcf'.format(account.object_id))
            else:
                self.insert_child(account.object_id, account, alias=account.carddav_uid)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == '.ctag'):
            return self.get_ctag_representation(self.get_ctag())
        elif (self.load_contents() and (auto_load_enabled)):
            if (name in ('.json', '.ls')):
                return self.get_collection_representation(name, self.get_children())
            elif (name == '.content.json'):
                return self.get_collection_representation(name, self.get_children(), rendered=True)
            else:
                result = self.get_child(name)
                if (result is not None):
                    return self.get_entity_representation(name, result, location='/dav/Contacts/{0}'.format(name),
                                                                         is_webdav=is_webdav)
        self.no_such_path()