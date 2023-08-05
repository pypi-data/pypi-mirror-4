#
# Copyright (c) 2010, 2012
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy         import *
from coils.core         import *
from keymap             import COILS_NOTE_KEYMAP

class SetObjectNotes(Command):
    __domain__ = "object"
    __operation__ = "set-notes"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.obj, object_id, x = self.get_object_id_from_parameters( **params )
        if not self.obj:
            self.obj   = self._ctx.type_manager.get_entity( object_id )
        self.notes = params.get( 'notes', [ ] )

    def check_run_permissions(self):
        # What rights should adjusting the linkage for an object actually required?  Note
        # that is isn't about adding a specific object link to an entity but adjust its
        # list of links, so this must come from an operation such as zOGI putObject.
        rights = self._ctx.access_manager.access_rights( self.obj, contexts=self.context_ids )
        if not set( 'wa' ).intersection( rights ):
            raise AccessForbiddenException( 'Insufficient access to {0}'.format( self.obj ) )

    def run(self, **params):
        notes = [ KVC.translate_dict( x, COILS_NOTE_KEYMAP ) for x in self.notes ]

        current = set( self.obj.notes.keys( ) )
        tmp = [ long( x[ 'object_id' ] ) for x in notes if long( x.get( 'object_id', 0 ) ) > 0 ]
        update_ids = set(tmp).intersection(set(current))
        delete_ids = current - set(tmp)

        updates = [ x for x in notes if x.get( 'object_id', 0 ) in update_ids ]
        inserts = [ x for x in notes if long( x.get('object_id', 0 ) ) == 0 ]
        deletes = delete_ids

        print inserts, updates, deletes

        # Deletes
        for object_id in deletes:
            # TODO: should we eat insufficient access exceptions?
            self._ctx.run_command('note::delete', id = object_id)

        # Adds
        for tmp in inserts:
            self._ctx.run_command('note::new', values=tmp,
                                                   context=self.obj)
        # Updates
        for tmp in updates:
            # TODO: should we eat insufficient access exceptions?
            object_id = int( tmp.get( 'object_id' ) )
            entity = self.obj.notes[object_id]
            self._ctx.run_command( 'note::set', values = tmp,
                                                object = self.obj.notes[object_id],
                                                context = self.obj )
        self.set_return_value( True )
