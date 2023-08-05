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
from sqlalchemy       import *
from coils.core       import *
from coils.core.logic import GetCommand, RETRIEVAL_MODE_SINGLE, RETRIEVAL_MODE_MULTIPLE

class GetAccount(GetCommand):
    __domain__ = "account"
    __operation__ = "get"

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        self._login = None
        if ('login' in params):
            self._login = params.get('login')

    def run(self, **params):
        db = self._ctx.db_session()
        if (self._login is not None):
            self.mode = RETRIEVAL_MODE_SINGLE
            self.log.debug('attempting to retrieve contact object with login of "{0}"'.format(self._login))
            query = db.query(Contact).filter(and_(Contact.login == self._login,
                                                  Contact.is_account == 1,
                                                  Contact.status != 'archived'))
        else:
            if (len(self.object_ids) == 0):
                self.mode = RETRIEVAL_MODE_SINGLE
                self.object_ids.append(self._ctx.account_id)
            query = db.query(Contact).filter(and_(Contact.object_id.in_(self.object_ids),
                                                   Contact.is_account == 1,
                                                   Contact.status != 'archived'))
        self.set_return_value(query.all())
