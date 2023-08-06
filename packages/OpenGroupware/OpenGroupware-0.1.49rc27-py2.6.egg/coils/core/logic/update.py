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
from set             import SetCommand

class UpdateCommand(SetCommand):

    def __init__(self):
        self.obj = None
        SetCommand.__init__(self)

    def set_last_modified(self):
        if (hasattr(self.obj, 'modified')):
            # HACK: In the case of a task the last_modified value is an int, not a datetime!
            # NOTE: This hack removed 2011-06-19 by hiding the last-modified field of the Job
            #       table as the "_modified" attribute and using a "modified" property that
            #       does the conversion back/forth between date-time and timestamp.
            #if (self.obj.__entityName__ == 'Task'):
            #    setattr(self.obj, 'modified',  self._ctx.get_timestamp())
            #else:
            setattr(self.obj, 'modified',  self._ctx.get_utctime())

    def audit_action(self):
        return
        log_entry = AuditEntry()
        log_entry.context_id = self.obj.object_id
        log_entry.action = '05_changed'
        log_entry.actor_id = self._ctx.account_id
        if (hasattr(self, 'message')):
            log_entry.message = self.message
        else:
            if (self._ctx.login is None):
                log_entry.message = '{0} changed by anonymous connection'.format(self.obj.__internalName__)
            else:
                log_entry.message = '{0} changed by {1}'.format(self.obj.__internalName__, self._ctx.get_login())
        self._ctx.db_session().add(log_entry)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.values = params.get('values', {})
        if ('object' in params):
            self.obj = params['object']
        elif ('id' in params):
            if (hasattr(self, 'get_by_id')):
                self.obj = self.get_by_id(int(params['id']), self.access_check)
                if (self.obj is None):
                    raise CoilsException('Command failed to load object for update by id.')
            else:
                raise CoilsException('Update command does not support by-id update')

    def increment_ctag(self):
        tags = self._ctx.db_session().query(CTag).\
                filter(CTag.entity==self.obj.__internalName__).all()
        if (tags):
            tags[0].ctag = tags[0].ctag + 1
        tags = None

    def run(self):
        if (self.obj is None):
            raise CoilsException('No object to update')
        try:
            self.obj.take_values(self.values, self.keymap)
        except Exception, e:
            self.log.error('Exception performing KVC take values for object update.')
            self.log.error('entity type:{0} values:{1}'.format(self.obj.__entityName__, self.values))
            self.log.exception(e)
            raise CoilsException('Exception performing KVC take values for object update.')
        
        self.increment_version()
        self.increment_ctag()
        self.set_last_modified()
        self.save_subordinates()
        self._result = self.obj
