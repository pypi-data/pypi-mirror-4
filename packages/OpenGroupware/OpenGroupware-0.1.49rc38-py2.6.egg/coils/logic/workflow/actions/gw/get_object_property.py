#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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

class GetObjectPropertyAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "get-object-property"
    __aliases__   = [ 'getObjectPropertyAction', 'getObjectProperty',  ]

    def __init__(self):
        ActionCommand.__init__( self )

    @property
    def result_mimetype(self):
        return self._mime_type

    def do_action(self):
        obj = self._ctx.type_manager.get_entity( self._object_id )
        if obj:
            prop = self._ctx.property_manager.get_property( obj, self._namespace, self._attribute )
            if prop:
                self.wfile.write( str( prop.get_value( ) ) )
            else:
                self.wfile.write( str( self._default_v ) )
        else:
            if self._default_v:
                self.wfile.write( str( self._default_v ) )
            else:
                raise AccessForbiddenException( 'Unable to marshall OGo#{0}'.format( self._object_id ) )

    def parse_action_parameters(self):
        self._object_id = self.process_label_substitutions( self.action_parameters.get( 'objectId', self.process.object_id ) )
        self._object_id = long( self._object_id )
        self._namespace = self.process_label_substitutions( self.action_parameters.get( 'namespace' ) )
        self._attribute = self.process_label_substitutions( self.action_parameters.get( 'attribute' ) )
        self._mime_type  = self.process_label_substitutions( self.action_parameters.get( 'mimeType', 'application/octet-stream' ) )
        self._default_v = self.process_label_substitutions( self.action_parameters.get( 'defaultValue', '' ) )

    def do_epilogue(self):
        pass
