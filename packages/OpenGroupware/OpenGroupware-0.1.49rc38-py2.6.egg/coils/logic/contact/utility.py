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
# TODO: Issue#97
import os
from coils.foundation import BLOBManager

def filename_for_vcard(object_id, version):
    return 'cache/vcard/{0}.{1}.vcf'.format(object_id, version)

def is_vcard_cached(object_id, version):
    return BLOBManager.Exists(filename_for_vcard(object_id, version))

def read_cached_vcard(object_id, version):
    handle = BLOBManager.Open(filename_for_vcard(object_id, version), 'r')
    if (handle is None):
        return None
    card = handle.read()
    BLOBManager.Close(handle)
    return card

def cache_vcard(object_id, version, vcf):
    filename = filename_for_vcard(object_id, version)
    handle = BLOBManager.Create(filename)
    handle.write(vcf)
    handle.flush()
    BLOBManager.Close(handle)
