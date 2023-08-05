#
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
import datetime, pprint, hashlib
from coils.net                         import DAVFolder, \
                                                OmphalosCollection, \
                                                OmphalosObject, \
                                                StaticObject, \
                                                EmptyFolder
from contactsfolder                    import ContactsFolder


class FavoritesFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def get_property_webdav_owner(self):
        return u'<href>/dav/Contacts/{0}.vcf</href>'.format(self.context.account_id)

    def _load_contents(self):
        self.insert_child('Contacts', ContactsFolder(self, 'Contacts', context=self.context,
                                                                       request=self.request))
        self.insert_child('Enterprises',  EmptyFolder(self, 'Enterprises', context=self.context,
                                                                           request=self.request))
        return True

    def object_for_keys(self, name, auto_load_enabled=True, is_webdav=False):
        if (auto_load_enabled): self.load_contents()
        if (self.is_loaded):
            result = self.get_child(name)
            if (result is not None):
                return result
        self.no_such_path()
