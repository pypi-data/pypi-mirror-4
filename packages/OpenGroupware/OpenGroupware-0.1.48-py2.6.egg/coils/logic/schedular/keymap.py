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
COILS_APPOINTMENT_KEYMAP = {
    'objectid':                 ['object_id', 'int', 0],
    'object_id':                ['object_id', 'int', 0],
    'parent_id':                ['parent_id', 'int', 0],
    'parentid':                 ['parent_id', 'int', 0],
    'owner_id':                 None,
    'ownerid':                  None,
    'ownerobjectid':            None,
    'readaccessteamobjectid':   ['access_id', 'int', 0],
    'access_id':                ['access_id', 'int', 0],
    'accessid':                 ['access_id', 'int', 0],
    'start':                    ['start', 'date'],
    'startdate':                ['start', 'date'],
    'end':                      ['end', 'date'],
    'enddate':                  ['end', 'date'],
    'cycle_end':                ['cycle_end_date', 'date'],
    'cycleend':                 ['cycle_end_date', 'date'],
    'cycle_type':               ['cycle_type'],
    'cycletype':                ['cycle_type'],
    'kind':                     ['kind'],
    'type':                     ['kind'],
    'title':                    ['title'],
    'resource_names':           ['resource_names', 'csv', ','],
    'location':                 ['location'],
    'keywords':                 ['keywords'],
    'comment':                  ['comment'],
    'notification':             ['notification', 'int', None],
    'notification_time':        ['notification', 'int', None],
    'notificationtime':         ['notification', 'int', None],
    'travel_duration_after':    ['prior_duration', 'int', 0],
    'travel_duration_before':   ['pre_duration', 'int', 0],
    'pre_duration':             ['pre_duration', 'int', 0],
    'prior_duration':           ['pre_duration', 'int', 0],
    'priorduration':            ['pre_duration', 'int', 0],
    'preduration':              ['pre_duration', 'int', 0],
    'conflict_disable':         ['is_conflict_disabled', 'int', 0],
    'write_ids':                ["write_access_list", 'cvs', ','],
    'participants':             None,
    'notes':                    None,
    'acls':                     None,
    'logs':                     None,
    'timezone':                 ['timezone', 'str', 'UTC'],
    'comment':                  ['comment', 'str', ''],
    'isallday':                 ['isAllDay', 'bool', False]
    }

COILS_PARTICIPANT_KEYMAP = {
    'entityname':               None,
    'firstname':                None,
    'lastname':                 None,
    'objectid':                 ['object_id', 'int', 0],
    'object_id':                ['object_id', 'int', 0],
    'participantentityname':    None,
    'participantobjectid':      ['participant_id', 'int', 0],
    'participant_id':           ['participant_id', 'int', 0],
    'participantid':            ['participant_id', 'int', 0],
    'company_id':               ['participant_id', 'int', 0],
    'companyid':                ['participant_id', 'int', 0],
    'rsvp':                     ['rsvp', 'int', 0],
    'comment':                  ['comment', 'str', '*BLANK COMMENT*'],
    'role':                     ['participant_role', 'str', 'REQ-PARTICIPANT'],
    'participant_role':         ['participant_role', 'str', 'REQ-PARTICIPANT'],
    'participantrole':          ['participant_role', 'str', 'REQ-PARTICIPANT'],
    'status':                   ['participant_status', 'str', 'NEEDS-ACTION'],
    'partstatus':               ['participant_status', 'str', 'NEEDS-ACTION'],
    'participant_status':       ['participant_status', 'str', 'NEEDS-ACTION'],
    'participantstatus':        ['participant_status', 'str', 'NEEDS-ACTION']
    }

COILS_RESOURCE_KEYMAP = {
    'objectid':                 ['object_id', 'int', 0],
    'object_id':                ['object_id', 'int', 0],
    'version':                  ['version', 'int', 0],
    'name':                     ['name'],
    'category':                 ['category'],
    'email':                    ['email'],
    'subject':                  ['subject'],
    'notification':             ['notification', 'int', 0],
    'notificationtime':         ['notification', 'int', 0]
    }
