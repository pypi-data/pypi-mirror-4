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
from keymap           import COILS_PARTICIPANT_KEYMAP

class EventMember(KVC):

    def __init__(self):
        self.participant_role   = 'REQ-PARTICIPANT'
        self.comment            = ''
        self.rsvp               = 0
        self.participant_status = 'NEEDS-ACTION'
        self.participant_id     = None
        self.appointment_id     = None


class SetParticipants(Command):
    """ Set the status, role, comment, and rsvp or a participant, or add a participant
        Supported parameters are: appointment [entity] OR appoinment_id [int] , status,
        role, comment, rsvp [int] """
    __domain__ = "appointment"
    __operation__ = "set-participants"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        # appointment_id is *ONLY* used to lookup the appointment, setting
        # self.appointment as if an appointment object was provided - that
        # happens in run().  Appointment id should *NOT* be used, always
        # reference self.appointment.object_id.
        Command.parse_parameters(self, **params)
        self.appointment    = params.get('appointment', None)
        self.appointment_id = params.get('appointment_id', None)
        self.participants   = params.get('participants', [])

    def map_participants(self):
        result = []
        self.participant_ids = []
        for participant in self.participants:
            x = EventMember()
            x.take_values(participant, COILS_PARTICIPANT_KEYMAP)
            x.appointment_id = self.appointment.object_id
            self.participant_ids.append(x.participant_id)
            result.append(x)
        self.participants = result

    def check_parameters(self):
        if ((self.appointment_id is None) and (self.appointment is None)):
            raise CoilsException('No appointment provided to set-participants')

    def run(self):
        db = self._ctx.db_session()
        self.check_parameters()
        self.map_participants()
        # If appointment wasn't provided, use appointment_id to look it up.
        if (self.appointment is None):
            self.appointment = self._ctx.run_command('appointment::get', id=int(self.appointment_id))
        if (self.appointment is None):
            raise 'Participant set cannot identify the relevant appointment'
        else:
            # TODO: Check for write access!
            self._result = True
        # Perform inserts and updates
        import pprint
        for x in self.participants:
            self.log.debug(pprint.pformat(x))
            for y in self.appointment.participants:
                self.log.debug(pprint.pformat(y))
                #print y
                #print x.participant_id, y.participant_id
                # HACK: We filter out processing NULL participant_ids.  These
                #        should not occur by we do see them occasionally in
                #        ancient OGo databases
                if (y.participant_id is not None):
                    if (x.participant_id == int(y.participant_id)):
                        y.take_values(x, None)
                        y._db_status = 'updated'
                        break
                else:
                    self.log.error('NULL participantId# encountered in appointmentId#{0}'.format(self.appointment.object_id))
            else:
                participant = Participant()
                participant.take_values(x, None)
                db.add(participant)
        # Perform deletes (use self.participant_ids, what isn't there wasn't in the set)
        query = db.query(Participant).filter(and_(Participant.appointment_id == self.appointment.object_id,
                                                   not_(Participant.participant_id.in_(self.participant_ids))))
        count = 0
        for x in query.all():
            db.delete(x)
            count = count + 1
        self.log.debug('{0} participants deleted from appointment.'.format(count))

