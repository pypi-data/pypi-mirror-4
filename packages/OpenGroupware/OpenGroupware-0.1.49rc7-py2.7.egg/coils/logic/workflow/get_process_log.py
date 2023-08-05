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
from time import time
from StringIO           import StringIO
from sqlalchemy         import and_
from coils.core         import *
from utility            import filename_for_process_log, \
                               read_cached_process_log, \
                               delete_cached_process_logs, \
                               cache_process_log

class GetProcessLog(Command):
    __domain__ = "process"
    __operation__ = "get-log"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.format   = params.get('format', 'text/plain')
        self.obj = params.get('process', params.get('object', None))
        if (self.obj is None):
            self.pid = params.get('pid', params.get('id', None))
        else:
            self.pid = self._obj.object_id
        if (self.pid is None):
            raise CoilsException('ProcessId required to retreive process OIE proprties')

    def run(self):
        
        # TODO: Support HTML & XML formats for response

        process = self._ctx.run_command( 'process::get', id=self.pid )
        if process:
            log_text = read_cached_process_log(process.object_id, process.version)
        else:
            raise CoilsException( 'Could not marshall specified process.' )

        db = self._ctx.db_session()
        
        if not log_text:
            # Render a Process Log
            query = db.query(ProcessLogEntry).\
                        filter(and_(ProcessLogEntry.process_id == self.pid,
                                     ProcessLogEntry.stanza != None)).\
                        order_by(ProcessLogEntry.timestamp)
                        
            content = StringIO( u'' )
            stanza = None
            start  = None
            for log in query.all( ):
                if stanza != log.stanza:
                    if stanza is not None:
                        content.write( u'\n' )
                    stanza = log.stanza
                    content.write( u'Stanza {0}\n'.format( stanza.strip( ) ) )
                category = log.category
                if category is None:
                    category = 'info'
                else:
                    category = category.strip( )
                    if category == 'start':
                        start = log.timestamp
                content.write( '{0}:{1}\n'.format( category.strip( ), log.message ) )
                if ( ( category == 'complete' ) and ( start is not None ) ):
                    content.write( 'duration:{0}s\n'.format( log.timestamp - start ) )
                    start = None
            log_text = content.getvalue( )
            content.close( )
            content = None
            cache_process_log( process.object_id, process.version, log_text )

        self.set_return_value( log_text )
