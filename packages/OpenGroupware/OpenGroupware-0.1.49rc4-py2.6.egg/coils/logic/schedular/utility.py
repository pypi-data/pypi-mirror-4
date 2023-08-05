#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core       import BLOBManager
from coils.foundation import UserDefaultsManager

def get_panel_ids(ctx, auth_id):
    #print 'Auth ID: {0}'.format(auth_id)
    ud = UserDefaultsManager(auth_id)
    # "scheduler_panel_accounts", "scheduler_panel_persons",
    # "scheduler_panel_teams", "scheduler_panel_resourceNames"
    ids = [ ]
    for object_id in ud.defaults().get('scheduler_panel_accounts', []):
        ids.append(int(object_id))
    for object_id in ud.defaults().get('scheduler_panel_persons', []):
        ids.append(int(object_id))
    for object_id in ud.defaults().get('scheduler_panel_teams', []):
        ids.append(int(object_id))
    if ('scheduler_panel_resourceNames' in ud.defaults()):
        resources = ctx.run_command('resource::get',
                                    names=ud.default_as_list('scheduler_panel_resourceNames'))
        if (resources is not None):
            for resource in resources:
                ids.append(resource.object_id)
    ids.append(auth_id)
    return ids


def get_panel(ctx, auth_id):
    ud = UserDefaultsManager(auth_id)
    # "scheduler_panel_accounts", "scheduler_panel_persons",
    # "scheduler_panel_teams", "scheduler_panel_resourceNames"
    items = [ ]
    object_ids = ud.defaults().get('scheduler_panel_accounts', [])
    items.extend(ctx.run_command('contact::get', ids=object_ids))
    object_ids = ud.defaults().get('scheduler_panel_persons', [])
    items.extend(ctx.run_command('contact::get', ids=object_ids))
    object_ids = ud.defaults().get('scheduler_panel_teams', [])
    items.extend(ctx.run_command('team::get', ids=object_ids))
    if ('scheduler_panel_resourceNames' in ud.defaults()):
        resources = ctx.run_command('resource::get',
                                    names=ud.defaults['scheduler_panel_resourceNames'])
        if (resources is not None):
            items.extend(resources)
    return items

#
# Process VEVENT caching
#

def filename_for_vevent(object_id, version):
    return 'cache/vevent/{0}.{1}.ics'.format(object_id, version)

def is_vevent_cached(object_id, version):
    return os.path.exists(filename_for_vcard(object_id, version))

def read_cached_vevent(object_id, version):
    handle = BLOBManager.Open(filename_for_vevent(object_id, version), 'r')
    if (handle is None):
        return None
    card = handle.read()
    BLOBManager.Close(handle)
    return card

def delete_cached_vevents():
    cached_vevents = BLOBManager.List('cache/vevent')
    for file in cached_vevents:
        BLOBManager.Delete('cache/vevent/' + file)

def cache_vevent(object_id, version, vcf):
    delete_cached_vevents()
    filename = filename_for_vevent(object_id, version)
    handle = BLOBManager.Create(filename)
    handle.write(vcf)
    handle.flush()
    BLOBManager.Close(handle)
