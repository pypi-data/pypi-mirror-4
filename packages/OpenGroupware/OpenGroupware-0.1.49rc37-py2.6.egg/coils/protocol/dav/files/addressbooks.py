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
import hashlib
from coils.core                        import Contact, Enterprise, CTag
from coils.net                         import DAVFolder, DAVObject, EmptyFolder
from csvobject                         import CSVObject

class AddressBooksFolder(DAVFolder):

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        self.insert_child('FavoriteContacts.txt', None)
        self.insert_child('AllContacts.txt', None)
        return True

    def _get_ctag_for_entity(self, entity):
        ''' Return a ctag appropriate for this object.
            Actual WebDAV objects should override this method '''
        db = self.context.db_session()
        query = db.query(CTag).filter(CTag.entity==entity)
        ctags = query.all()
        if (len(ctags) == 0):
            return None
        query = None
        return ctags[0].ctag

    def _ctag_for_enumeration(self, enumeration):
        m = hashlib.md5()
        for entry in enumeration:
            m.update('{0}:{1}'.format(entry[0], entry[1]))
        return m.hexdigest()

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == 'FavoriteContacts.txt'):
            contents = self.context.run_command('contact::get-favorite', properties=[Contact.object_id, Contact.version])
            contents.sort()
            ctag = self._ctag_for_enumeration(contents)
            return CSVObject(self, name, command='contact::get-favorite',
                                          ctag=ctag,
                                          context=self.context,
                                          request=self.request)
        elif (name == 'AllContacts.txt'):
            ctag = self._get_ctag_for_entity('Person')
            return CSVObject(self, name, command='contact::list',
                                          ctag=ctag,
                                          context=self.context,
                                          request=self.request)
        self.no_such_path()