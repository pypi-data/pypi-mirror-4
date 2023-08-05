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
import urllib
from coils.net   import DAVFolder, DAVObject, EmptyFolder

class TeamsFolder(DAVFolder):

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_self(self):
        self.data = { }
        try:
            teams = self.context.run_command('team::get')
            for team in teams:
                self.data[urllib.quote(team.name)] = [team]
        except Exception, e:
            self.log.exception(e)
            return False
        else:
            return True

    def object_for_key(self, name):
        if (self.load_self()):
            if (name in self.data):
                x = EmptyFolder(self,
                                name,
                                entity=self.data[name][0],
                                context=self.context,
                                request=self.request)
                return x
            elif (urllib.quote(name) in self.data):
                name = urllib.quote(name)
                x = EmptyFolder(self,
                               name,
                               entity=self.data[name][0],
                               context=self.context,
                               request=self.request)
                return x
        return self.no_such_path()