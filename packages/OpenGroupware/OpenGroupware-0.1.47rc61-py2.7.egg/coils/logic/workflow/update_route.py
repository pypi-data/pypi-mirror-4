#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.foundation    import *
from coils.core.logic    import UpdateCommand
from keymap              import COILS_ROUTE_KEYMAP
from utility             import filename_for_route_markup

class UpdateRoute(UpdateCommand):
    __domain__ = "route"
    __operation__ = "set"

    def __init__(self):
        UpdateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap =  COILS_ROUTE_KEYMAP
        self.entity = Route
        UpdateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        UpdateCommand.parse_parameters(self, **params)
        if ('markup' in params):
            self.values['markup'] = params['markup']

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('route::get', id=object_id,
                                                      access_check=access_check)

    def save_route_markup(self):
        if (self.obj.get_markup() is not None):
            handle = BLOBManager.Create(filename_for_route_markup(self.obj), encoding='binary')
            handle.write(self.obj.get_markup())
            BLOBManager.Close(handle)

    def run(self):
        UpdateCommand.run(self)
        if ('markup' in self.values):
            self.obj.set_markup(self.values['markup'])
        if ('keep' in self.values):
            if (self.values.get('keep', False)):
                value = 'YES'
            else:
                value = 'NO'
            self._ctx.property_manager.set_property(self.obj,
                                                    'http://www.opengroupware.us/oie',
                                                    'preserveAfterCompletion',
                                                    value)
        self.save_route_markup()
        self._result = self.obj
