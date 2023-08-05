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
from coils.foundation    import *
from coils.core          import *

class DeleteParticipants(Command):
    __domain__ = "appointment"
    __operation__ = "delete-participants"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.obj = params.get('object', None)
        self.appointment_id = params.get('id', None)

    def run(self):
        self._result = False
        db = self._ctx.db_session()
        if ((self.obj is None) and (self.appointment_id is not None)):
            self.obj = self._ctx.run_command('appointment::get', id=self.appointment_id)
            if (self.obj is None):
                raise CoilsException('Unable to marshall specified appointment for deletion.')
        elif (self.obj is None):
            raise CoilsException('No Appointment provided to deletion.')
        query = db.query(Participant).filter(Participant.appointment_id==self.obj.object_id)
        for participant in query.all():
            self._ctx.db_session().delete(participant)
        self._result = True
