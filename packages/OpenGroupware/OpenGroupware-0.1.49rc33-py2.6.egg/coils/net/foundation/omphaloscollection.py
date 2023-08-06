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
import json, yaml
from datetime            import datetime
# Core
from coils.core            import *
import coils.core.omphalos as omphalos
import coils.core.xml      as omphalos_xml
# DAV Classses
from davobject           import DAVObject

class OmphalosCollection(DAVObject):
    """ Represents an OpenGroupware entity in a DAV collection,  a GET will return the
        representation of the object - vCard, vEvent, vToDo, etc... """

    # The self.data in a DAVObject  to be a first-class ORM entity
    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        self.render_mode = params.get('rendered', False)
        #self.detail      = int(params.get('detailLevel', 2973))
        self.detail      = int(params.get('detailLevel', 0))

    def _encode(self, o):
        if (isinstance(o, datetime)):
            return  o.strftime('%Y-%m-%dT%H:%M:%S')
        raise TypeError()

    def do_GET(self):
        if (self.render_mode):
            result = omphalos.Render.Results(self.data, self.detail, self.context)
        else:
            # Return to client as an index
            result = []
            for entry in self.data:
                if (isinstance(entry, list)):
                    entity = entry[0]
                else:
                    entity = entry
                if (entity.version is None):
                    version = 0
                else:
                    version = entity.version
                displayName = ''
                if (hasattr(entity, 'get_display_name')):
                    displayName = entity.get_display_name()
                result.append({'objectId': entity.object_id,
                               'entityName': entity.__entityName__,
                               'displayName': displayName,
                               'version': version})
        json_data = json.dumps(result, default=self._encode)
        result = None
        self.request.simple_response(200,
                                     data=json_data,
                                     mimetype='application/json')
        json_data = None
