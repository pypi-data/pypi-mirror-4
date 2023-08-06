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
import json
from StringIO            import StringIO
import yaml              as yaml
from datetime            import datetime
# Core
from coils.core          import *
import coils.core.omphalos as omphalos
import coils.core.xml      as omphalos_xml
# DAV Classses
from davobject          import DAVObject

class OmphalosObject(DAVObject):
    """ Represents an OpenGroupware entity in a DAV collection,  a GET will return the
        representation of the object - vCard, vEvent, vToDo, etc... """

    # The self.data in a DAVObject  to be a first-class ORM entity
    def __init__(self, parent, name, **params):
        #self.location = None
        DAVObject.__init__(self, parent, name, **params)

    def _encode(self, o):
        if (isinstance(o, datetime)):
            return  o.strftime('%Y-%m-%dT%H:%M:%S')
        raise TypeError()

    def do_GET(self):
        if (self.name[-5:] == '.json'):
            result  = omphalos.Render.Result(self.entity, 65503, self.context)
            payload = json.dumps(result, default=self._encode)
            mimetype = u'text/plain'
        elif (self.name[-5:] == '.yaml'):
            result  = omphalos.Render.Result(self.entity, 65503, self.context)
            payload = yaml.dump(result)
            mimetype = u'text/plain'
        elif (self.name[-4:] == '.xml'):
            payload  = omphalos_xml.Render.render(self.entity, self.context, detailLevel=65503)
            mimetype = u'application/xml'
        result = None
        self.request.simple_response(200,
                                     data=payload,
                                     mimetype=mimetype,
                                     headers={ 'X-COILS-OBJECT-ID': self.entity.object_id } )
        payload = None
