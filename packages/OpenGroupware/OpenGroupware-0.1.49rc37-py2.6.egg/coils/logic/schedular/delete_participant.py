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
from coils.core.logic    import DeleteCommand
from keymap              import COILS_PARTICIPANT_KEYMAP

class DeleteParticipant(DeleteCommand):
    __domain__ = "participant"
    __operation__ = "delete"

    def __init__(self):
        DeleteCommand.__init__(self)

    def parse_parameters(self, **params):
        DeleteCommand.parse_parameters(self, **params)
        if (self.obj is None):
            self.appointment = params.get('appointment', None)
            self.appointment_id = params.get('appointment_id', None)
            self.participant_id = params.get('participant_id', None)

    def run(self, **params):
        if (self.obj is None):
            db = self._ctx.db_session()
            if ((self.appointment_id is None) and (self.appointment is not None)):
                appointment_id = self.appointment.object_id
            elif (self.appointment_id is not None):
                appointment_id = self.appointment_id
            else:
                raise CoilsException('No appointment specified for participant deletion')
            if (self.participant_id is None):
                raise CoilsException('No participant specified for participant deletion')
            query = db.query(Participant).filter(and_(Participant.appointment_id==appointment_id,
                                                       Participant.participant_id==self.participant_id))
            self.obj = query.first()
            if (self.obj is None):
                raise CoilsException('Unable to resolve participant for deletion.')
        DeleteCommand.run(self)

