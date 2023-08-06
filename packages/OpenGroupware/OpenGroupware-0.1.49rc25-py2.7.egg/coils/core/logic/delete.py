#
# Copyright (c) 2009, 2012
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
from sqlalchemy.orm.collections import InstrumentedList, MappedCollection

BASIC_TYPES = ( basestring, int, float, datetime, type(None) )

class DeleteCommand(Command):

    def __init__(self):
        Command.__init__(self)
        self._result = True

    def parse_parameters(self, **params):
        self.obj = None
        Command.parse_parameters(self, **params)
        if ('object' in params):
            self.obj = params.get('object', None)
        elif ('id' in params):
            self.obj = self.get_by_id(int(params.get('id')), self.access_check)
        if (self.obj is None):
            raise CoilsException('Delete command invoked with no object')

    def audit_action(self):
        object_id = None
        if hasattr(self, 'obj'):
            if hasattr(self.obj, 'object_id'):
                object_id = self.obj.object_id
        if object_id:
            log_entry = AuditEntry()
            log_entry.context_id = object_id
            log_entry.action = '99_delete'
            log_entry.actor_id = self._ctx.account_id
            if (hasattr(self, 'message')):
                log_entry.message = self.message
            else:
                if (self._ctx.login is None):
                    log_entry.message = '{0} deleted by anonymous connection'.format(self.entity_name)
                else:
                    log_entry.message = '{0} deleted by {1}'.format(self.obj.__entityName__, self._ctx.get_login())
            self._ctx.db_session().add(log_entry)

    def delete_subordinates(self):
        #TODO: SQLalchemy should do most of this for us
        subs = [ 'acls', 'addresses', 'company_values', 'properties', 'telephones',
                 'contacts', 'enterprises', 'projects' ]
        for sub in subs:
            if hasattr( self.obj, sub ):
                self.log.debug('Deleting {0} for objectId#{1}'.format(sub, self.obj.object_id))
                e = getattr(self.obj, sub)
                if isinstance( e, InstrumentedList ):
                    for x in e:
                        self.delete_object_info( x )
                        self._ctx.db_session().delete( x )
                elif isinstance( e, MappedCollection ):
                    for x in e.values():
                        self.delete_object_info( x )
                        self._ctx.db_session().delete( x )  
                elif type(e) in BASIC_TYPES:
                    pass
                else:
                    raise CoilsException('Encountered subordinate "{0}" of unknown type "{1}"'.format(sub, type(e)))

    def delete_notes(self):
        # TODO: This needs love, how does the notation file get deleted?
        if hasattr( self.obj, 'notes' ):
            notes = getattr( self.obj, 'notes' )
            for note in notes:
                if (((note.project_id == self.object_id) and (note.company_id is None) and (note.project_id is None)) or
                    ((note.project_id is None) and (note.company_id == self.object_id) and (note.project_id is None)) or
                    ((note.project_id is None) and (note.company_id is None) and (note.project_id == self.object_id))):
                    self.delete_object_info(note)
                    self._ctx.db_session().delete(note)

    def increment_ctag(self):
        tags = self._ctx.db_session().query(CTag).\
                filter(CTag.entity==self.obj.__internalName__).all()
        if (tags):
            tags[0].ctag = tags[0].ctag + 1
        tags = None

    def delete_object_info(self, e):
        if (hasattr(e, 'object_id')):
            self._ctx.type_manager.purge_cache(e.object_id)
            self._ctx.db_session().\
                query(ObjectInfo).\
                filter(ObjectInfo.object_id == e.object_id).\
                delete(synchronize_session='fetch')

    def delete(self):
        self.delete_subordinates()
        self.delete_object_info(self.obj)
        self._ctx.flush()
        self._ctx.db_session().delete(self.obj)

    def epilogue(self):
        Command.epilogue(self)
        Command.notify(self)
        self.obj = None

    def run(self):
        self.entity_name = self.obj.__internalName__
        self.object_id = self.obj.object_id
        self.increment_ctag()
        self.delete()
        self.set_return_value(True)
