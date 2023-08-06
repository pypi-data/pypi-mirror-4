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

class SetFavorite(Command, ContactCommand):
    __domain__ = "contact"
    __operation__ = "set-favorite"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        if ('ids' in params):
            self.object_ids = [int(x) for x in params.get('ids')]
        elif ('objects' in params):
            self.object_ids = [int(x.object_id) for x in params.get('objects')]
        else:
            raise CoilsException('No ids or objects parameter provided to contact::set-favorite')

    def run(self):
        self._ctx.set_favorited_ids_for_kind('Contact', self.object_ids)
