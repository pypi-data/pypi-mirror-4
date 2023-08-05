#
# Copyright (c) 2010, 2012
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
from datetime         import datetime, timedelta
from sqlalchemy       import *
from coils.foundation import *
from coils.core       import *

class SetCommand(Command):
    '''
    Base command for performing an update, applying new values, to an
    entity.  The Create command descends from this and overrides the
    required bits to apply the same operations when creating a new
    entity.  This command requires a "values" dictionary that either
    corresponds to the ORM model or is Omphalos.
    '''

    def __init__(self):
        self.values = None
        self._acls_from_client_saved = None
        Command.__init__(self)

    def save_acls(self):
        '''
        Record the ACLs, if provided, on the Set operation, provided that
        the entity in question supports ACL.
        '''
        if hasattr( self.obj, 'acls' ):
            acls = KVC.subvalues_for_key( self.values, [ '_ACCESS', 'acls' ] )
            if acls:
                self._ctx.run_command( 'object::set-access', object=self.obj, acls=acls )
                self._acls_from_client_saved = True
            else:
                self._acls_from_client_saved = False

    @property
    def acls_from_client_saved(self):
        '''
        Report if the set operation has performed an ACL sync from the 
        provided values.
        TODO: What is this used for?  and where?
        '''
        return self._acls_from_client_saved

    def save_notes(self):
        if not isinstance( self.obj, Task ):
            if hasattr( self.obj, 'notes' ):
                inbox = KVC.subvalues_for_key( self.values, [ '_NOTES', 'notes' ], default=None )
                if inbox is not None:
                    self._ctx.run_command( 'object::set-notes', object=self.obj, notes=inbox )
        else:
            # Task notes are not notes, but are task comments, so this
            # hack avoids this anomoly in the data model
            pass

    def save_links(self):
        '''
        Save the object links, if provided in values, to the object.
        '''
        link_list = KVC.subvalues_for_key( self.values, [ '_OBJECTLINKS', 'objectlinks' ], default=None )
        # This must be an is-not-none check, not merely a not check, since an empty
        # list has meaning - it means to delete all links.  A None means that the 
        # values did not include object link information.
        if link_list is not None:
            self._ctx.run_command( 'object::set-links', object=self.obj, links=link_list )

    def save_properties(self):
        '''
        Save the provided, if provided, object property information.
        '''
        if hasattr( self.obj, 'properties' ):
            properties = KVC.subvalues_for_key( self.values, [ '_PROPERTIES', 'properties' ], None)
            if properties is not None:
                self._ctx.property_manager.set_properties(self.obj, properties)

    def increment_version(self):
        self.increment_object_version(self.obj)

    def increment_object_version(self, obj):
        if (hasattr(obj, 'version')):
            if (obj.version is None):
                obj.version = 1
            else:
                obj.version += 1

    def save_subordinates(self):
        self.save_acls()
        self.save_notes()
        self.save_properties()

    def epilogue(self):
        # NOTE: Updating the object info needs to be almost the very last thing we do so as to insure
        #       we get the best data possible
        Command.epilogue(self)
        Command.update_object_info(self)
        Command.notify(self)
