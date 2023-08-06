#
# Copyright (c) 2011 Morrison Industries
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
from coils.core import ServerDefaultsManager, CoilsException

class BEBAPI(object):

    def __init__(self, context):
        self.context = context
        self._sd     = None

    @property
    def server_defaults(self):
        if not self._sd:
            self._sd = ServerDefaultsManager()
        return self._sd

    @property
    def protocol_defaults(self):
        try:
            return self.server_defaults.default_as_dict('BEBRPCConfig')
        except:
            raise CoilsException('BEB-RPC protocol bundle is not configured (lookup "BEBRPCConfig" in WMOGAG)')

    def translate_context_specification(self, cid):
        trans_table = self.protocol_defaults.get('ContextTable', { })
        if (cid in trans_table):
            return [int(x) for x in trans_table.get(cid)]
        else:
            if (self.protocol_defaults.get('AllowSearchContextFallThrough', 'NO') == 'YES'):
                return self.context.context_ids
        raise CoilsException('Cannot translate BEB context string "{0}" to an OpenGroupware context'.format(cid))