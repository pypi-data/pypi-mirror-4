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
from     render_object import *
from render_contact import *

def render_team(entity, detail, ctx):
    """ {'entityName': 'Team',
         'memberObjectIds': [9144860, 1013530, 1138130, 1125360, 26850, 27190],
         'name': 'Morrison Industries (MI)',
         'objectId': 970730,
         'objectVersion': 5,
         'ownerObjectId': 10000}"""
    # TODO: Implement
    team = { 'entityName': 'Team',
             'name': as_string(entity.name),
             'objectId': entity.object_id,
             'objectVersion': as_integer(entity.version),
             'ownerObjectId': as_integer(entity.owner_id) }
    expand = True
    if (entity.object_id == 10003):
        sd = ServerDefaultsManager()
        expand = sd.bool_for_default('zOGIExpandAllIntranet')
        sd = None
    if (expand):
        if ((detail & 128) or (detail & 256)):
            if (detail & 128):
                # Include members in 'memberObjectIds' attribute
                # TODO: Implement conflict detection
                team['memberObjectIds'] = []
                for member in entity.members:
                    team['memberObjectIds'].append(member.child_id)
            if (detail & 256):
                # Include members in _CONTACTS
                team['_CONTACTS'] = []
                for member in entity.members:
                    contact = ctx.run_command('contact::get', id=member.child_id)
                    if (contact is not None):
                        team['_CONTACTS'].append(render_contact(contact, 0, ctx))
    return render_object(team, entity, detail, ctx)
