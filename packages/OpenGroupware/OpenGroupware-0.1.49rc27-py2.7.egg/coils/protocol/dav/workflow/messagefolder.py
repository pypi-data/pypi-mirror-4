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
# THE SOFTWARE.
#
from coils.core                         import *
from coils.net                          import *
from messageobject                      import MessageObject
from workflow                           import WorkflowPresentation

class MessageFolder(DAVFolder, WorkflowPresentation):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self.process_id = self.entity.object_id

    @property
    def label_type(self):
        return 'uuid'

    def _load_contents(self):
        self.log.debug('Returning enumeration of messages of process {0}.'.format(self.process_id))
        messages = self.get_process_messages(self.entity)
        for message in messages:
            self.insert_child(message.uuid.strip()[1:-1], message)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        self.log.debug('Request for folder key {0}'.format(name))
        if (self.load_contents()):
            if (self.has_child(name)):
                return MessageObject(self,
                                      name,
                                      entity=self.get_child(name),
                                      parameters=self.parameters,
                                      process=self.entity,
                                      context=self.context,
                                      request=self.request)
        raise NoSuchPathException('Not such path as %s' % self.request.path)