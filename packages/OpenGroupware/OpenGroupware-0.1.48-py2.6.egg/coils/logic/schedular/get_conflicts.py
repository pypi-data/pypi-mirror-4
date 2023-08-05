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
from datetime           import datetime, timedelta
from sqlalchemy         import *
from coils.foundation  import *
from coils.core         import *

class GetConflicts(Command):
#TODO: Only works in appointment-mode,  that is, when an appointment
#       is provided as a parameter.  Not sure if there is another mode.
    __domain__ = "schedular"
    __operation__ = "get-conflicts"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def prepare(self, ctx, **params):
        self.start = datetime.today()
        self.span  = timedelta(days=30)
        self.end   = self.start + self.span
        self.parts = [ ]
        self.objid = 0
        self.names = [ ] # resource names
        self._result = { }
        Command.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if (params.has_key('start')):
            self.start = params['start']
        # SPAN
        if (params.has_key('span')):
            x = params['span']
            self.span  = timedelta(days=x)
            self.end   = self.start + self.span
        # END (Overrides span)
        if (params.has_key('end')):
            self.end = params['end']
        # PARTICIPANTS
        if (params.has_key('participants')):
            x = params['participants']
            if (isinstance(x, list)):
                for p in x:
                    if (hasattr(p, 'object_id')):
                        self.parts.append(p.object_id)
        else:
            self.parts.append(self._ctx.account_id)
        # RESOURCES ? (Ugh, the stupid by-name thing)
        # APPOINTMENT (Overides all the above!)
        if (params.has_key('appointment')):
            x = params['appointment']
            self.objid = x.object_id
            self.start = x.start
            self.end   = x.end
            for p in x.participants:
                if ((p.participant_status != 'DECLINED') or
                    (p.participant_role   != 'NON-PARTICIPANT')):
                    self.parts.append(p.participant_id)
            for n in x.get_resource_names():
                self.names.append(n)

    def flatten_teams(self):
        # FLATTEN TEAMS
        tm = self._ctx.type_manager
        index = tm.group_ids_by_type(self.parts)
        if (index.has_key('Team')):
            teams = self._ctx.run_command('team::get', ids=index['Team'],
                                                       access_check=False)
            for team in teams:
                for member in team.members:
                    if (member.child_id not in self.parts):
                        self.parts.append(member.child_id)

    def participant_conflict_query(self):
        db = self._ctx.db_session()
        query = db.query(Appointment, Participant).\
            filter(Appointment.object_id==Participant.appointment_id).\
            filter(and_(Appointment.object_id !=  self.objid,
                         Appointment.status != 'archived',
                         Appointment.end > self.start,
                         Appointment.start < self.end,
                         or_(Appointment.conflict_disable is None,
                             Appointment.conflict_disable == 0),
                         and_(Participant.participant_id.in_(self.parts),
                              Participant.participant_status != 'DECLINED',
                              Participant.participant_role != 'NON-PARTICIPANT')))
        return query

    def resource_conflict_query(self):
        pass

    def add_conflict(self, appointment, participant):
        if (not self._result.has_key(appointment)):
            self._result[appointment] = [ ]
        self._result[appointment].append(participant)

    def run(self):
        self.flatten_teams()
        # SELECT PARTICIPANT CONFLICTS
        query = self.participant_conflict_query()
        data = query.all()
        for appointment, participant in data:
            self.add_conflict(appointment, participant)
        return