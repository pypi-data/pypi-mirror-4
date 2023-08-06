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
from coils.core.logic    import ActionCommand

class GrantAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "grant-access"
    __aliases__   = [ 'grantAction', 'grant' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        self._ctx.run_command('object::set-acl', object=self.process,
                                                 context_id = self._context_id,
                                                 action = self._action,
                                                 permissions = self._permissions)

    def parse_action_parameters(self):
        self._context_id = int(self.action_parameters.get('contextId'))
        # TODO: verify that "action" is either "allowed" or "denied"
        self._action     = self.action_parameters.get('action', 'allowed')
        # TODO: verify sanity of resulting permissions string.
        # Valid entity permission flags are:
        #  r = read   [Implies "lv" for Process entities]
        #  w = write  [modify; also implies insert for Process entities]
        #  l = list   [implied by "r" for Process entities]
        #  d = delete [synonymous with t + x]
        #  a = administer
        #  k = create [Not applicable to Process entities]
        #  t = delete object
        #  x = delete container [Owner of Process is the owner of the Route?]
        #  i = insert [Implied by "w" for Process entities]
        #  v = view   [Implied by "r" for Process entities]

        if ('permissions' in self.action_parameters):
            self._permissions = self.action_parameters.get('permissions').lower().strip()
        else:
            # TODO: Should we somehow support granting of the admin privilege?
            #        What does "admin" mean in relation to a process?
            if (self.action_parameters.get('write', 'NO').upper() == 'YES'):
                self._permissions = 'wvrlid'
            elif (self.action_parameters.get('read', 'NO').upper() == 'YES'):
                self._permissions = 'rvl'
            else:
                self._permissions = 'vl'

    def do_epilogue(self):
        pass
