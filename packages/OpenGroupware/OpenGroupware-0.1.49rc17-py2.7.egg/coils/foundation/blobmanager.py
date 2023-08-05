#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import codecs, os, foundation, shelve, pickle
from datetime            import datetime
from tempfile            import SpooledTemporaryFile
from foundation          import STORE_ROOT
from dbfs1               import DBFS1Manager


def blob_manager_for_ds(sky_url, project_id=None):
    if (sky_url is None):
        return DBFS1Manager(project_id)
    driver = sky_url.split(':')[0]
    if (driver == 'skyrix'):
        return DBFS1Manager(project_id)
    elif (driver == 'file'):
        return SkyFSManager(sky_url)
    raise 'Unknown Data Store driver type of {0}'.format(driver)

class BLOBManager(object):

    __slots__ = ()

    @staticmethod
    def _path_from_name(name):
        if (isinstance(name, tuple)):
            return u'{0}/{1}/{2}'.format(foundation.STORE_ROOT, name[0], name[1])
        return u'{0}/{1}'.format(foundation.STORE_ROOT, name)

#
# Raw filesystem support
#

    @staticmethod
    def Create(name, encoding='utf-8', version=None):
        if (isinstance(name, tuple) or isinstance(name, list)):
            path = foundation.STORE_ROOT
            for chunk in name[:-1]:
                path = u'{0}/{1}'.format(path, chunk)
                if (os.path.exists(path)):
                    pass
                else:
                    os.makedirs(path)
            filename = u'{0}/{1}'.format(path, name[-1:][0])
        else:
            filename = u'{0}/{1}'.format(foundation.STORE_ROOT, name)
        if (encoding == 'binary'):
            return open(filename, 'w+b')
        else:
            # TODO: (?) Use codecs.EncodedFile(file, input[, output[, errors]])
            return codecs.open(filename, 'w+', encoding=encoding)

    @staticmethod
    def Open(name, mode, encoding='utf-8', version='0', create=False):
        filename = u'{0}/{1}'.format(foundation.STORE_ROOT, name)
        if (os.path.exists(filename)):
            if (encoding == 'binary'):
                return open(filename, mode + 'b')
            else:
                # TODO: (?) Use codecs.EncodedFile(file, input[, output[, errors]])
                return codecs.open(filename, mode, encoding=encoding)
        elif (create):
            return BLOBManager.Create(name.split('/'), encoding=encoding, version=version)
        return None

    @staticmethod
    def Close(handle):
        if (handle is not None):
            handle.close()

    @staticmethod
    def Delete(name, version='0'):
        if name is None:
            raise Exception('Request to delete an object without name.')
        filename = u'{0}/{1}'.format(foundation.STORE_ROOT, name)
        if (os.path.exists(filename)):
            os.remove(filename)
            return True
        return False

    @staticmethod
    def ScratchFile(suffix='.data'):
        return SpooledTemporaryFile(max_size=65535,
                                     prefix='Coils.',
                                     suffix=suffix,
                                     dir=u'{0}/tmp'.format(foundation.STORE_ROOT))

    @staticmethod
    def List(name):
        return os.listdir('{0}/{1}'.format(foundation.STORE_ROOT, name))

    @staticmethod
    def SizeOf(name, version='0'):
        return os.path.getsize(BLOBManager._path_from_name(name))

    @staticmethod
    def Exists(name, version='0'):
        return os.path.exists(BLOBManager._path_from_name(name))
        
        
    @staticmethod
    def Created(name):
        return datetime.fromtimestamp(os.path.getctime(BLOBManager._path_from_name(name)))
        
    @staticmethod
    def Modified(name):
        return datetime.fromtimestamp(os.path.getmtime(BLOBManager._path_from_name(name)))

#
# Shelf support
#

    @staticmethod
    def OpenShelf(uuid=None, create=False):
        # CLUSTER-TODO
        # TODO: What can go wrong here?  We should be catching some exceptions.
        filepath = '{0}/shelves/{1}.shelve'.format(foundation.STORE_ROOT, str(uuid))
        if (create):
            if (os.path.exists(filepath)):
                os.remove(filepath)
        shelf = shelve.open(filepath, flag='c', protocol=pickle.HIGHEST_PROTOCOL)
        return shelf

    @staticmethod
    def DeleteShelf(uuid=None):
        filepath = '{0}/shelves/{1}.shelve'.format(foundation.STORE_ROOT, str(uuid))
        if (os.path.exists(filepath)):
            os.remove(filepath)
            return True
        return False
