#
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
#
import os, time
from sqlalchemy       import and_
from coils.foundation import *
from coils.core       import *
from utility          import *


class ContactCacheService(Service):
    __service__       = 'coils.contacts.cache'
    __auto_dispatch__ = True
    __is_worker__     = True

    def __init__(self):
        self._cursor     = None
        self._iter       = 0
        self._next_run   = 0.0
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self._ticktock = time.time()
        self._ctx = AdministrativeContext()

    @property
    def ticktock(self):
        if ((time.time() - selk._ticktock) > 59):
            self._ticktock = time.time()
            return True
        return False
        
    def _read_data(self):
        self.log.info('Retrieving Contact list for vCard cache fill.')
        query = self._ctx.db_session().\
                          query(Contact.object_id, Contact.version).\
                          filter(and_(Contact.status != 'archived',
                                       Contact.first_name is not None,
                                       Contact.last_name is not None)).distinct()
        self._cursor = query.all()
        self._iter   = 0

    def work(self):
        if (time.time() > self._next_run):
            if (self._cursor is None):
                self._read_data()
                self._count = len(self._cursor)
            else:
                if (self._iter >= self._count):
                    self.log.info('Refill of vCard cache complete.')
                    self._cursor = None
                    # schedule a run in 12 hours
                    self._next_run = (time.time() + 43200.0)
                    return
                else:
                    self.log.debug('Walking contact cache; items {0}...{1}'.format(self._iter, self._iter + 150))
                    for i in range(150):
                        if (self._iter < self._count):
                            if not is_vcard_cached(self._cursor[self._iter].object_id,
                                                    self._cursor[self._iter].version):
                                self._ctx.run_command('contact::get-as-vcard',
                                                      id=self._cursor[self._iter].object_id,
                                                      access_check=False)
                            self._iter   =  self._iter + 1
                        else:
                            break
