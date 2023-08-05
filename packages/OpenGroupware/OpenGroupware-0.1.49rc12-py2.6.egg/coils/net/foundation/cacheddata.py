#
# Copyright (c) 2009 , 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import base64, shutil, os
from coils.core          import *

FS=chr(28) # Field seperator
GS=chr(29) # Group seperator
RS=chr(30) # Record seperator

class CachedData(object):

    def __init__(self, sid, path, ctag):
        self._sid  = str(sid)
        self._path = str(path)
        self._ctag = str(ctag)
        self.open_cache()

    @property
    def sid(self):
        return self._sid

    @property
    def path(self):
        return self._path

    @property
    def ctag(self):
        return self._ctag

    def _get_path(self):
        filename = FS.join([self.sid, self.path])
        filename = base64.encodestring(filename).strip()
        filename = '{0}/{1}/{2}'.format(filename[0:3], filename[3:6], filename)
        filename = 'cache/dav/{0}'.format(filename)
        return filename

    def _write_header(self, handle):
        handle.seek(0)
        # Write a type 01 record; format of type 01 is: sid, path, ctag
        record = ('01', self.sid, self.path, self.ctag)
        header = (FS.join(record) + RS).ljust(511, '~') + RS
        handle.write(header)

    def _read_header(self, handle):
        # Returns a tuple of cid, path, ctag
        # May return None, None, None if the cache was void

        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        #self.log.debug('Cached data file size: {0}'.format(size))
        if (size > 512):
            handle.seek(0)
            header = handle.read(512)
            if (header[511] == RS):
                record, rs, fill = header.partition(RS)
                record = record.split(FS)
                if (record[0] == '01'):
                    # Type 01 records have a format of: cid, path, ctag
                    return record[1], record[2], record[3]
                else:
                    raise CoilsException('Unrecognized cache header version for {0}:{1}'.format(self.sid, self.path))
            else:
                raise CoilsException('Mangled header in cached data object for {0}:{1}'.format(self.sid, self.path))
        else:

            return None, None, None

    def open_cache(self):
       self._handle = BLOBManager.Open(self._get_path(), 'r+', encoding='binary', create=True)

    def close_cache(self):
        self._handle.close()

    @property
    def is_current(self):
        sid, path, ctag = self._read_header(self._handle)
        if (sid is None):
            return False
        elif (sid == self.sid and path == self.path and ctag == self.ctag):
            return True
        else:
            return False

    @property
    def not_current(self):
        return not self.is_current

    @property
    def size(self):
        self._handle.seek(0, os.SEEK_END)
        size = self._handle.tell()
        return size - 512

    def prepare(self):
        self._write_header(self._handle)

    def write_from_stream(self, rfile):
        self._write_header(self._handle)
        data = rfile.read(4096)
        while (data != ''):
            self._handle.write(data)
            data = rfile.read(4096)
        self._handle.flush()

    def get_stream(self):
        self._handle.seek(512)
        return self._handle
