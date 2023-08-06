#
# Copyright (c) 2009, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from utility            import filename_for_process_markup

class GetProcess(GetCommand):
    __domain__ = "process"
    __operation__ = "get"

    def set_markup(self, processes):
        result = [ ]

        for process in processes:
            try:
                handle = BLOBManager.Open(filename_for_process_markup(process), 'rb', encoding='binary')
            except IOError, e:
                # Process will be dropped from the result; most likely this process has been deleted
                self.log.error('Unable to load process markup for processId#{0}'.format(process.object_id))
                continue
            else:
                if (handle is not None):
                    bpml = handle.read()
                    process.set_markup(bpml)
                    BLOBManager.Close(handle)
                    result.append(process)

        return result


    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if 'guid' in params:
            self.query_by = 'guid'
            self.guid = params[ 'guid' ]

    def run(self, **params):
        db = self._ctx.db_session()

        if self.query_by == 'object_id':
            if self.object_ids:
                query = db.query( Process ).filter( Process.object_id.in_( self.object_ids ) )
        elif self.query_by == 'guid':
            query = db.query( Process ).filter( Process.uuid == self.guid )
            self.set_single_result_mode( )
        else:
            self.set_multiple_result_mode()
            query = db.query(Process).filter(Process.owner_id.in_(self._ctx.context_ids))

        self.set_return_value(self.set_markup(query.all()))

