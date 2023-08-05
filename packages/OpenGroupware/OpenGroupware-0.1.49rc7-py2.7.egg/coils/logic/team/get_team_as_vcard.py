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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from coils.core.vcard   import Render
from get_team           import GetTeam

class GetTeamAsVCard(GetTeam):
    __domain__ = "team"
    __operation__ = "get-as-vcard"
    mode = None

    def parse_parameters(self, **params):
        if ('object' in params):
            self._object = params.get('object')
        else:
            GetTeam.parse_parameters(self, **params)

    def run(self):
        if (hasattr(self, '_object')):
            self._result = Render.render(self._object, self._ctx)
        else:
            GetTeam.run(self)
            if (self._result is None):
                return
            elif (isinstance(self._result, list)):
                teams = self._result
                self._result = []
                for team in teams:
                    self._result.append(Render.render(team, self._ctx))
            else:
                self._result = Render.render(self._result, self._ctx)