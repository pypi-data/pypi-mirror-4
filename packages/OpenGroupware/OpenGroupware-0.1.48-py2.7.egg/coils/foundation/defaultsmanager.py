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
import os, codecs
from plist       import PListParser, PListWriter
from picklejar   import PickleParser, PickleWriter
from blobmanager import BLOBManager
from defaults    import COILS_DEFAULT_DEFAULTS

class DefaultsManager(object):
    __encoding__     = "ISO8859-1"

    def __init__(self):
        pass

    def sync(self):
        return False

    def defaults(self):
        return self._defaults

    def is_default_defined(self, default):
        return (default in self._defaults)

    def set_default_value(self, default, value):
        self._defaults[default] = value

    def get_default_value(self, default, fallback=None):
        if (default in self._defaults):
            return self._defaults[default]
        if (fallback is None):
            raise Exception('No such default as {0}'.format(default))
        else:
            return fallback

    def bool_for_default(self, default):
        value = self._defaults.get(default, 'NO')
        if (value == 'YES'):
            return True;
        return False

    def string_for_default(self, default, value = ''):
        return str(self._defaults.get(default, value))

    def integer_for_default(self, default, value = 0):
        return int(self._defaults.get(default, value))

    def default_as_dict(self, default):
        value = self.get_default_value(default)
        if (isinstance(value, dict)):
            return value
        raise 'Improperly structured default; {0} is not a dictionary.'.format(default)

    def default_as_list(self, default, fallback=None):
        value = self.get_default_value(default, fallback)
        if (isinstance(value, list)):
            return value
        raise 'Improperly structured default; {0} is not a list.'.format(default)

    def update_defaults(self):
        pass
        

class UserDefaultsManager(DefaultsManager):

    def __init__(self, account_id):
        DefaultsManager.__init__(self)
        self._account_id = account_id
        self._defaults = self._read_user_defaults()

    def sync(self):
        self._defaults = self._write_user_defaults()
        return True

    def _read_user_defaults(self):
        plist = BLOBManager.Open('documents/{0}.defaults'.format(self._account_id),
                                 'rb',
                                 encoding=DefaultsManager.__encoding__)
        if (plist is not None):
            data = plist.read()
            plist.close()
            defaults = PListParser().propertyListFromString(data)
        else:
            # TODO: Support template defaults!
            defaults = {}
        return defaults

    def _write_user_defaults(self):
        old_defaults = self._read_user_defaults()
        for key in self._defaults.keys():
            old_defaults[key] = self._defaults[key]
        writer = PListWriter()
        data = writer.store(old_defaults)
        plist = BLOBManager.Open('documents/{0}.defaults'.format( self._account_id),
                                 'wb',
                                 encoding=DefaultsManager.__encoding__,
                                 create=True)
        plist.write(data)
        plist.close()
        return old_defaults


class ServerDefaultsManager(DefaultsManager):

    def __init__(self):
        DefaultsManager.__init__(self)
        self._defaults = self._read_server_defaults()

    def _read_server_defaults(self):
        # TODO: Optimize, server backend should only read these once or when hup'd
        blob = BLOBManager.Open('.server_defaults.pickle',
                                 'rb',
                                 encoding='binary')
        if (blob is not None):
            data = blob.read()
            blob.close()
            defaults = PickleParser().propertyListFromString(data)
        else:
            blob = BLOBManager.Open('.libFoundation/Defaults/NSGlobalDomain.plist',
                                     'rb',
                                      encoding=DefaultsManager.__encoding__)
            if (blob is not None):
                data = blob.read()
                blob.close()
                defaults = PListParser().propertyListFromString(data)
            else:
                raise Exception('Unable to load server defaults; file {0} does not exist.')
        # The Obj/C OGo includes default defaults, or values for defaults if no site specific defaults
        # are defined.  We need merge these values into site define defaults.
        for key in COILS_DEFAULT_DEFAULTS:
            if (key not in defaults):
                defaults[key] = COILS_DEFAULT_DEFAULTS[key]
        return defaults

    def add_server_default(self, key, value):
        COILS_DEFAULT_DEFAULTS[key] = value

    @property
    def orm_dsn(self):
        #postgres://OGo@127.0.0.1/OGo
        conndict = self.default_as_dict('LSConnectionDictionary')
        return 'postgresql://{0}@{1}:{2}/{3}'.format(conndict.get('userName'),
                                                      conndict.get('hostName'),
                                                      conndict.get('port'),
                                                      conndict.get('databaseName'))

    @property
    def orm_logging(self):
        if self.bool_for_default('PGDebugEnabled'):
            return True
        return False
