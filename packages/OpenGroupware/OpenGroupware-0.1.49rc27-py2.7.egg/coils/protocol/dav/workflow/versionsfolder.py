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
import os
from coils.core                        import *
from coils.net                         import *
from bpmlobject                        import BPMLObject
from yamlobject                        import YAMLObject
from utility                           import route_versions, \
                                                process_versions

class VersionsFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def supports_PUT(self):
        return True

    def _load_contents(self):
        self.data = { }
        if (isinstance(self.entity, Route)):
            for edition in route_versions(self.entity):
                name = '{0}.{1}.bpml'.format(self.entity.name, edition)
                self.insert_child(name, BPMLObject(self, name, entity=self.entity,
                                                         version=edition,
                                                         context=self.context,
                                                         request=self.request))
        elif (isinstance(self.entity, Process)):
            for edition in process_versions(self.entity):
                name = '{0}.{1}.yaml'.format(self.entity.object_id, edition)
                self.insert_child(name, YAMLObject(self, name, entity=self.entity,
                                                         version=edition,
                                                         context=self.context,
                                                         request=self.request))
        else:
            return False
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (self.load_contents()):
            if (self.has_child(name)):
                return self.get_child(name)
        raise self.no_such_path()