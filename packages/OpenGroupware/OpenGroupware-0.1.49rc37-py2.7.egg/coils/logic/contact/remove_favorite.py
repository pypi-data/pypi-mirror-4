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
#
from coils.core          import *
from coils.logic.address import GetCompany
from command             import ContactCommand

class RemoveFavorite(Command, ContactCommand):
    __domain__ = "contact"
    __operation__ = "remove-favorite"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        self.object_id = int(params.get('id'))

    def run(self):
        favorite_ids = self.get_favorite_ids()
        self.log.debug(favorite_ids)
        if (self.object_id in favorite_ids):
            favorite_ids.remove(self.object_id)
            self.set_favorite_ids(favorite_ids)
            self.log.debug('objectId#{0} remvoed from favorite contacts of objectId#{1}'.\
                format(self.object_id, self._ctx.account_id))
        else:
            self.log.debug('objectId#{0} was not a favorite contact of objectId#{1}'.\
                format(self.object_id, self._ctx.account_id))
