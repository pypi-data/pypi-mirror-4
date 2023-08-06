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
from coils.foundation   import *
from coils.core         import *
from coils.core.logic   import GetCommand
from utility            import get_panel_ids
from command            import AppointmentCommand

"""
Input:
    parts = [10100, 27190]
    start = datetime(year=2008,month=1,day=1,hour = 0, minute = 0, second = 0)
    end = datetime(year=2009, month=12, day=31, hour=12, minute=59, second = 59)
    names = ['GRD Classroom']  # Resource names
    kinds = ['meetings','outward']
Query:
SELECT  ...
FROM date_x
  JOIN date_company_assignment ON date_x.date_id = date_company_assignment.date_id
  LEFT OUTER JOIN object_acl AS object_acl_1 ON object_acl_1.object_id = date_x.date_id
WHERE date_x.db_status != 'archived'
  AND date_x.end_date > '2008-01-01 00:00:00'
  AND date_x.start_date < '2009-12-31 12:59:59'
   AND date_x.apt_type IN ('meeting','outward')
   AND (date_company_assignment.company_id IN (10100,27190)
        OR date_x.resource_names = 'GRD Classroom'
        OR date_x.resource_names ILIKE 'GRD Classroom,%'
        OR date_x.resource_names ILIKE '%,GRD Classroom,%'
        OR date_x.resource_names ILIKE '%,GRD Classroom')
ORDER BY object_acl_1.auth_id
"""

# Parameters:
#   access_check
#   start (defaults to today)
#   span: value in days, defaults to 8 days
#   end: defaults to 8 days from today, this value overrides span
#   participants: ids of participants, can include resources
#   resources: names of resources, either an array or a CSV
#   kinds: types of appointments, either an array or a CSV

class GetAppointmentRange(GetCommand, AppointmentCommand):
    __domain__ = "appointment"
    __operation__ = "get-range"

    def __init__(self):
        GetCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.start = datetime.today()
        self.span  = timedelta(days=8)
        self.end   = self.start + self.span
        self.parts = [ ]
        self.names = None
        self.kinds = None
        self.mode  = 2
        GetCommand.prepare(self, ctx, **params)

    def set_assumed_participants(self):
        self.parts.append(self._ctx.account_id)

    def parse_parameters(self, **params):
        # NOTE: We don't call our parent GetCommand's parse_parameters, we skip over it
        # and go straight for the generic Command's parse_parameters;  that gives us the
        # access_check parameter, we don't need GetCommand's id/ids parameters.
        Command.parse_parameters(self, **params)
        if (bool(params.get('visible_only', False))): self._required_right = 'v'
        else: self._required_right = 'l'
        self.parse_range(start = params.get('start', None),
                         end   = params.get('end', None),
                         span  = params.get('span', None))
        # PARTICIPANTS
        self.parse_participants(participants = params.get('participants', None),
                                exclude      = params.get('exclude', None),
                                resources    = params.get('resources', None))
        # KINDS (types)
        self.parse_kinds(kinds = params.get('kinds', None))

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

    def parse_participants(self, participants=None, exclude=None, resources=None):
        # TODO: Implement exluding participants
        if (participants is None):
            self.log.debug('no participants specified, assuming panel.')
            self.set_assumed_participants()
        else:
            # TODO: These needs a rigourous test-case
            if (isinstance(participants, list)):
                for p in participants:
                    if (hasattr(p, 'object_id')): self.parts.append(p.object_id)
                    elif (isinstance(p, int)): self.parts.append(p)
            kinds = self._ctx.type_manager.group_ids_by_type(self.parts)
            if (kinds.has_key('Resource')):
                if (self.names is None): self.names = []
                name_list = self._ctx.run_command('resource::get-names', ids=kinds['Resource'])
                self.log.debug('converted participant ids {0} into resource names {1}.'.format(kinds['Resource'],
                                                                                               name_list))
                if (name_list is not None):
                    for name in name_list: self.names.append(name)
                # Remove the object ids of Resource entities from the participants list.
                for object_id in kinds['Resource']: self.parts.remove(object_id)
                self.log.debug('removed resource object ids from participant list')
        self.flatten_teams()
        # Named resources (the "resources' param)
        if (resources is None):
            pass
        else:
            # TODO: Finish implementation of Resource participants
            if (self.names is None): self.names = []
            if (isinstance(resources, list)):
                self.names.extend(params['resources'])
            else:
                self.names.extend(params['resources'].split(','))

    def parse_kinds(self, kinds=None):
        if (kinds is None): pass
        else:
            if (isinstance(kinds, list)):
                self.kinds = params['kinds']
            else:
                self.kinds = []
                for kind in kinds.split(','):
                    self.kinds.append(kind.lower().strip())


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

    def get_query(self):
        db = self._ctx.db_session()
        query = db.query(Appointment)
        query = query.join(Participant)
        query = query.join(DateInfo)
        query = query.filter(Appointment.status != 'archived')
        query = query.filter(Appointment.end > self.start)
        query = query.filter(Appointment.start < self.end)
        # Kinds
        if (self.kinds is not None):
            query = query.filter(Appointment.kind.in_(self.kinds))
        # Participants
        participant_clause = or_()
        self.log.debug('participants: {0}'.format(self.parts))
        participant_clause.append(Participant.participant_id.in_(self.parts))
        if (self.names is not None):
            participant_clause.append(self.get_resource_filter())
        query = query.filter(participant_clause)
        return query

    def get_resource_filter(self):
        if (self.names is None):
            return None
        outer = or_()
        for name in self.names:
            inner = or_()
            inner.append(Appointment._resource_names == name)
            inner.append(Appointment._resource_names.ilike('%s,%%' % name))
            inner.append(Appointment._resource_names.ilike('%%,%s,%%' % name))
            inner.append(Appointment._resource_names.ilike('%%,%s' % name))
            outer.append(inner)
        return outer

    def add_result(self, appointment):
        if (appointment not in self._result):
            self._result.append(appointment)

    def run(self):
        query = self.get_query()
        self.set_return_value(self.load_special_values(query.all()), right=self._required_right)


class GetAppointmentOverviewRange(GetAppointmentRange):
    __domain__ = "appointment"
    __operation__ = "get-overview-range"

    def set_assumed_participants(self):
        self.parts.extend(get_panel_ids(self._ctx, self._ctx.account_id))
