#
# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import os
from coils.core          import *
from coils.core.logic    import ActionCommand
from utility             import sql_connect

class ExecuteAction(ActionCommand):
    __domain__    = "action"
    __operation__ = "sql-execute"
    __aliases__   = [ 'sqlExecuteAction', 'sqlExecute' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        db = sql_connect(self._source)
        cursor = db.cursor()
        try:
            cursor.execute(self._query)
        except Exception, e:
            self.log_message('Database error encountered executing statement:\n{0}'.format(self._query),
                             category='error')
            raise e
            
        cursor.close()
        if (self._commit == 'YES'):
            db.commit()
        db.close()

    def parse_action_parameters(self):
        self._source  = self.action_parameters.get('dataSource', None)
        self._query   = self.action_parameters.get('queryText', None)
        self._commit  = self.action_parameters.get('doCommit', 'YES').upper()
        if (self._source is None):
            raise CoilsException('No source defined for executeAction')
        if (self._query is None):
            raise CoilsException('No query defined for executeAction')
        else:
            self._query = self.decode_text(self._query)
        self._query = self.process_label_substitutions(self._query)            

    def do_epilogue(self):
        pass
        
