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
from datetime           import datetime, timedelta
from sqlalchemy         import *
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import GetCommand

# Parameters:
#   access_check
#   start (defaults to today)
#   span: value in days, defaults to 8 days
#   end: defaults to 8 days from today, this value overrides span
#   participants: ids of participants, can include resources
#   resources: names of resources, either an array or a CSV
#   kinds: types of appointments, either an array or a CSV

class GetProcessRange(GetCommand):
    __domain__ = "process"
    __operation__ = "get-range"

    def __init__(self):
        GetCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.start = datetime.today()
        self.span  = timedelta(days=8)
        self.end   = self.start + self.span
        self.set_multiple_result_mode()
        GetCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        # NOTE: We don't call our parent GetCommand's parse_parameters, we skip over it
        # and go straight for the generic Command's parse_parameters;  that gives us the
        # access_check parameter, we don't need GetCommand's id/ids parameters.
        Command.parse_parameters(self, **params)
        self.parse_range(start = params.get('start', None),
                         end   = params.get('end', None),
                         span  = params.get('span', None))

    def parse_range(self, start=None, end=None, span=None):
        # Start
        if (start is None):
            self.start = self._ctx.get_utctime() - timedelta(days=1)
        else:
            self.start = start
        # Span (this value will be discarded if an end value was specified)
        if (span is None):
            # TODO: What is the legacy default for this value (time span for appointment rainge)?
            self.span = timedelta(days=45)
        else:
            self.span  = timedelta(days=int(span))
            self.end   = self.start + self.span
        # End
        if (end is None): self.end = self.start + self.span
        else: self.end = end

    def get_query(self):
        db = self._ctx.db_session()
        query = db.query(Process)
        query = query.filter(Process.created > self.start)
        query = query.filter(Process.created < self.end)
        return query

    def run(self):
        query = self.get_query()
        self.set_return_value(query.all())