#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import uuid
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render


class CreateCollection(ActionCommand):
    __domain__ = "action"
    __operation__ = "create-collection"
    __aliases__   = [ 'createCollection', 'createCollectionAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def read_omphalos_entities(self):
        f.seek(0)
        for event, element in etree.iterparse(self._rfile, events=("start", "end")):
            if (event == 'start') and (element.tag == 'entity'):
                object_id = None
                entity_name = None
            elif (event == 'end') and (element.tag == 'entity'):
                yield element.attrib.get('objectId'), element.attrib.get('entityName')
                element.clear()

    def do_action(self):
        assignments = [ ]
        for object_id, entity_name in self.read_omphalos_entities():
            assignments.append( { 'objectId': int(object_id) } )
        collection = self._ctx.run_command('collection::new',
                                           values = { 'name': self._collection_name,
                                                      'dav_enabled': self._webdav_enabled },
                                           assignments = assignments )


    @property
    def result_mimetype(self):
        return 'plain/text'

    def parse_action_parameters(self):
        self._collection_name = self.action_parameters.get('collectionName', str(uuid.uuid()))
        self._collection_name = self.process_label_substitutions(self._collection_name)
        self._webdav_enabled  = self.action_parameters.get('webDAVEnabled', 'NO')
        self._webdav_enabled = self.process_label_substitutions(self._webdav_enabled)

    def do_epilogue(self):
        pass
