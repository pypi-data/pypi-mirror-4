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
from sqlalchemy       import *
from coils.core       import *
from coils.foundation import *
from globals         import *

class SetParticipant(Command):
    """ Set the status, role, comment, and rsvp or a participant, or add a participant
        Supported parameters are: appointment [entity] OR appoinment_id [int] , status,
        role, comment, rsvp [int] """
    __domain__ = "participant"
    __operation__ = "set"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.appointment = params.get('appointment', None)
        self.appointment_id = params.get('appointment_id', None)
        self.status = params.get('status', None)
        self.role = params.get('role', None)
        self.comment = params.get('comment', None)
        self.participant_id = params.get('participant_id', None)
        self.rsvp = params.get('rsvp', None)

    def polish_parameters(self):
        if (self.status is not None):
            self.status = self.status.upper().strip()
        if (self.role is not None):
            self.role = self.role.upper().strip()
        if (self.comment is not None):
            self.comment = self.comment.strip()

    def check_parameters(self):
        if ((self.status is not None) and (self.status not in COILS_PARTICIPANT_STATUS)):
            raise CoilsException('Undefined participant status in participation update')
        if ((self.role is not None) and (self.role not in COILS_PARTICIPANT_ROLES)):
            raise CoilsException('Undefined participant role in participation update')
        # TODO: Check that rsvp is either 0 or 1
        # TODO: Check that participant is either a contact or a team
        # TODO: Check comment for maximum length

    def run(self):
        self.polish_parameters()
        self.check_parameters()
        self._result = False
        if (self.participant_id is None):
            raise 'No participant identified for participant update'
        if ((self.appointment is None) and (self.appointment_id is not None)):
            self.appointment = self._ctx.run_command('appointment::get', id=int(self.appointment_id))
        if (self.appointment is None):
            raise 'Participant set cannot identify the relevant appointment'
        else:
            # TODO: Check for write access!
            self._result = True
        values = {'appointment_id': int(self.appointment_id),
                  'participant_id': int(self.participant_id) }
        if (self.role    is not None): values['participant_role']   = self.role
        if (self.comment is not None): values['comment']            = self.comment
        if (self.status  is not None): values['participant_status'] = self.status
        if (self.rsvp    is not None): values['rsvp']               = int(self.rsvp)
        for participant in self.appointment.participants:
            if (participant.participant_id == int(self.participant_id)):
                participant.take_values(values, COILS_PARTICIPANT_STATUS)
                # Maintain the legacy db_status field, which is confusing in this case
                # because of the existance of the participant status value.
                participant._db_status = 'updated'
                break
        else:
            db = self._ctx.db_session()
            participant = Participant()
            participant.take_values(values, COILS_PARTICIPANT_STATUS)
            db.add(participant)
