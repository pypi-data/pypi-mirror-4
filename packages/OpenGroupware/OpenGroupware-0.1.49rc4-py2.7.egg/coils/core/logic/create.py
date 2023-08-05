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
from coils.foundation import AuditEntry
from coils.core       import *
from set             import SetCommand

class CreateCommand(SetCommand):

    def __init__(self):
        self.values = None
        SetCommand.__init__(self)

    def prepare(self, ctx, **params):
        Command.prepare(self, ctx, **params)
        if ((self.entity is None) or (self.keymap is None)):
            raise CoilsException('Create command object not properly initialized')
        return

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('values' in params):
            self.values = params['values']
        else:
            raise CoilsException('Create command executed with no \'values\' parameter!')

    def set_version(self):
        if hasattr(self.obj, 'version'):
            setattr(self.obj, 'version', 1)

    def set_owner(self):
        if hasattr(self.obj, 'owner_id'):
            setattr(self.obj, 'owner_id', self._ctx.account_id)

    def set_created(self):
        utc_time =  self._ctx.get_utctime()
        if hasattr(self.obj, 'created'):
            if getattr(self.obj, 'created') is None:
                setattr(self.obj, 'created',  utc_time)
        if hasattr(self.obj, 'modified'):
            if getattr(self.obj, 'modified') is None:
                setattr(self.obj, 'modified',  utc_time)

    def set_object_id(self):
        if hasattr(self.obj, 'object_id'):
            i = self._ctx.db_session().execute(Sequence('key_generator'))
            setattr(self.obj, 'object_id', i)
            self.log.debug('Assigned objectId#{0} to new {1}'.format(i, self.obj.__entityName__))

    def audit_action(self):
        if hasattr(self.obj, 'object_id'):
            log_entry = AuditEntry()
            log_entry.context_id = self.obj.object_id
            log_entry.action = '00_created'
            log_entry.actor_id = self._ctx.account_id
            if hasattr(self, 'message'):
                log_entry.message = self.message
            else:
                if self._ctx.login is None:
                    log_entry.message = '{0} created by anonymous connection'.format(self.obj.__internalName__)
                else:
                    if hasattr(self.obj, 'get_display_name'):
                        log_entry.message = '{0}#{1} "{2}" created by "{3}"'.\
                            format(self.obj.__entityName__,
                                   self.obj.object_id,
                                   self.obj.get_display_name(),
                                   self._ctx.get_login())
                    else:
                        log_entry.message = '{0}#{1} created by "{1}"'.\
                            format(self.obj.__entityName__,
                                   self.obj.object_id,
                                   self._ctx.get_login())
            self._ctx.db_session().add(log_entry)

    def increment_ctag(self):
        tags = self._ctx.db_session().query(CTag).\
                filter(CTag.entity==self.obj.__internalName__).all()
        if (tags):
            tags[0].ctag = tags[0].ctag + 1
        tags = None

    def save(self):
        self._ctx.db_session().add(self.obj)
        self.update_object_info()

    def run(self):
        self.obj = self.entity()
        try:
            self.obj.take_values(self.values, self.keymap)
        except Exception, e:
            self.log.error('Exception performing KVC take values for object creation.')
            self.log.error('entity type:{0} values:{1}'.format(self.obj.__entityName__, self.values))
            self.log.exception(e)
            raise CoilsException('Exception performing KVC take values for object creation.')
        self.set_object_id()
        self.set_version()
        self.set_owner()
        self.set_created()
        self.increment_ctag()
        self.save_subordinates()
        self._result = self.obj
