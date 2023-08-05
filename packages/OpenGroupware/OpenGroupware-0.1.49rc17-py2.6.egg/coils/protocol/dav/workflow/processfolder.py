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
# THE SOFTWARE.
#
from coils.core                       import *
from coils.net                        import *
from messagefolder                    import MessageFolder
from labelfolder                      import LabelFolder
from bpmlobject                       import BPMLObject
from messageobject                    import MessageObject
from signalobject                     import SignalObject
from versionsfolder                   import VersionsFolder
from proplistobject                   import PropertyListObject
from processlogobject                 import ProcessLogObject

class ProcessFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)
        self.entity = params['entity']
        self.process_id = self.entity.object_id

    @property
    def label_type(self):
        return 'label'

    def _load_contents(self):
        self.insert_child('Messages', None)
        self.insert_child('Labels', None)
        self.insert_child('input', None)
        self.insert_child('markup.xml', None)
        self.insert_child('Versions', None)
        self.insert_child('propertyList.txt', None)
        self.insert_child('log.html', None)
        if (self.entity.completed is not None):
            if (self.entity.state == 'C'):
                self.insert_child('output', None)
            else:
                self.insert_child('exception', None)
        return True

    def get_input_message(self):
        return self.context.run_command('process::get-input-message', process=self.entity)

    def get_output_message(self):
        if (self.entity.completed is None):
            return None
        return self.context.run_command('process::get-output-message', process=self.entity)

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        self.log.debug('Request for folder key {0}'.format(name))
        if (name == 'Messages'):
            return MessageFolder(self, name,
                                  entity=self.entity,
                                  parameters=self.parameters,
                                  context=self.context,
                                  request=self.request)
        elif (name == 'Labels'):
            return LabelFolder(self, name,
                                entity=self.entity,
                                parameters=self.parameters,
                                context=self.context,
                                request=self.request)
        elif (name in ['input', 'output', 'exception']):
            if ((name in ['output', 'exception']) and (self.entity.output_message is None)):
                self.no_such_path()
            if ((name == 'input') and (self.entity.input_message is None)):
                self.no_such_path()
            if (name == 'exception'):
                message = getattr(self, 'get_output_message'.format(name))()
            else:
                message = getattr(self, 'get_{0}_message'.format(name))()
            return MessageObject(self, name,
                                  entity=message,
                                  parameters=self.parameters,
                                  process=self.entity,
                                  context=self.context,
                                  request=self.request)
        elif (name == 'markup.xml'):
            return BPMLObject(self, name,
                               entity=self.entity,
                               context=self.context,
                               request=self.request)
        elif (name == 'log.html'):
            return ProcessLogObject(self, name,
                                     entity=self.entity,
                                     context=self.context,
                                     request=self.request)
        elif (name == 'signal'):
            return SignalObject(self, name,
                                parameters=self.parameters,
                                entity=self.entity,
                                context=self.context,
                                request=self.request)
        elif (name == 'propertyList.txt'):
            return PropertyListObject(self, name,
                                entity=self.entity,
                                context=self.context,
                                request=self.request)
        elif (name == 'Versions'):
            return VersionsFolder(self, name,
                                   parameters=self.parameters,
                                   entity=self.entity,
                                   context=self.context,
                                   request=self.request)
        self.no_such_path()
