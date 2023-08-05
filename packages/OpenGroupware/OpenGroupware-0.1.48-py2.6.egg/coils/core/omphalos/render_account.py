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
# THE SOFTWARE.
#
from render_object import *
from render_contact import *
from render_timezone import *

def build_calendar_panel(defaults, ctx):
    # "scheduler_panel_accounts", "scheduler_panel_persons",
    # "scheduler_panel_teams", "scheduler_panel_resourceNames"
    ids = [ ]
    for account in defaults.get('scheduler_panel_accounts', []):
        ids.append(int(account))
    for contact in defaults.get('scheduler_panel_persons', []):
        ids.append(int(contact))
    for team in defaults.get('scheduler_panel_teams', []):
        ids.append(int(team))
    if ('scheduler_panel_resourceNames' in defaults):
        resources = ctx.run_command('resource::get',
                                    names=defaults['scheduler_panel_resourceNames'])
        if (resources is not None):
            for resource in resources:
                ids.append(resource.object_id)
    return ids

def render_account(entity, defaults, detail, ctx, favorite_ids=[]):
    if (detail & 256):
        a = render_contact(entity, detail, ctx, favorite_ids=favorite_ids)
    else:
        a = { 'objectId': entity.object_id,
              'entityName': 'Account',
              'version': entity.version,
              'login': entity.login }
        if (detail & 2):
            a['_OBJECTLINKS'] = render_object_links(entity, ctx)
        if (detail & 16):
            a['_PROPERTIES'] = render_object_properties(entity, ctx)
    if ('timezone' in defaults):
        tz = render_timezone(defaults['timezone'], ctx)
        is_tz_set = 1
    else:
        tz = render_timezone('GMT', ctx)
        is_tz_set = 0
    if (defaults.has_key('scheduler_ccForNotificationMails')):
        cc = defaults['scheduler_ccForNotificationMails']
    else:
        cc = None
    a['_DEFAULTS'] = { 'entityName': 'defaults',
                       'accountObjectId': entity.object_id,
                       'calendarPanelObjectIds': build_calendar_panel(defaults, ctx),
                       'appointmentReadAccessTeam': 0,
                       'appointmentWriteAccess': [],
                       'notificationCC': as_string(cc),
                       'secondsFromGMT': as_integer(tz['offsetFromGMT']),
                       'isDST': as_integer(tz['isCurrentlyDST']),
                       'timeZone': as_string(tz['abbreviation']),
                       'timeZoneName': as_string(tz['description']),
                       'isTimeZoneSet': as_integer(is_tz_set) }
    return a