#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime            import datetime, timedelta
from pytz                import timezone
from sqlalchemy          import *
from sqlalchemy.orm      import *
from coils.foundation    import *
from coils.core          import *
from coils.logic.address import SearchCompany
from keymap              import COILS_CONTACT_KEYMAP

"""
Input:
    criteria = [ { 'value':, 'conjunction':, 'key':, 'expression': EQUALS | LIKE | ILIKE } ... ]
    limit = #
    debug = True / False
    access_check = True / False
"""

class SearchContacts(SearchCompany):
    __domain__ = "contact"
    __operation__ = "search"
    mode = None

    def __init__(self):
        SearchCompany.__init__(self)

    def prepare(self, ctx, **params):
        SearchCompany.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCommand.parse_parameters(self, **params)

    def add_result(self, contact):
        if (contact not in self._result):
            self._result.append(contact)

    def do_revolve(self):
        enterprises = [ ]
        for contact in self._result:
            for assignment in contact.enterprises:
                if (int(assignment.parent_id) not in enterprises):
                    enterprises.append(int(assignment.parent_id))
        return self._ctx.run_command('enterprise::get', ids=enterprises)

    def run(self):
        self._query = self._parse_criteria(self._criteria, Contact, COILS_CONTACT_KEYMAP)
        import time
        start = time.time()
        data = self._query.all()
        print '----'
        print time.time() - start
        self.log.debug('query returned %d objects' % len(data))
        self.set_return_value(data)
        return
