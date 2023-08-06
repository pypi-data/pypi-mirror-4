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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetMessage(Command):
    __domain__ = "message"
    __operation__ = "get"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._scope = params.get('scope', [])
        if ('uuid' in params):
            self.uuid = params['uuid']
        elif (('label' in params) and (('process' in params) or
                                        ('pid' in params))):
            self.uuid = None
            self.label = params['label']
            if ('process' in params):
                self.pid = params['process'].object_id
            else:
                self.pid = int(params['pid'])
        else:
            raise CoilsException('message::get parameters do not identify a message.')

    def run(self):
        db = self._ctx.db_session()
        if (self.uuid is not None):
            # Message requested by UUID, we know exactly what to look for.
            query = db.query(Message).filter(Message.uuid==self.uuid)
            data = query.all()
        else:
            # Message requested by label, we will work backwards through the scope until we
            # find a so labelled message.
            scopes = self._scope[:] # Copy the scope list
            scopes.reverse()        # Reverse the scope list, search inner to outer
            scopes.append(None)    # Make the outermost scope the global scope
            for scope in scopes:
                self.log.debug('Search for label {0} in scope {1}'.format(self.label, scope))
                query = db.query(Message).filter(and_(Message.label == self.label,
                                                       Message.process_id == self.pid,
                                                       Message.scope == scope))
                data = query.all()
                if (len(data) > 0):
                    break;
        data = self._ctx.access_manager.filter_by_access('r', data)
        if (len(data) > 0):
            self._result = data[0]
        else:
            self._result = None
