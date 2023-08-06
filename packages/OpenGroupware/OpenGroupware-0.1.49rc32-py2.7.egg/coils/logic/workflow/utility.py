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
# TODO:
import os, datetime
from copy               import deepcopy
from coils.foundation   import BLOBManager
from coils.core         import CoilsException

def filename_for_message_text(uuid):
    return 'wf/m/{0}'.format(unicode(uuid))

def filename_for_deleted_message_text(uuid):
    return 'wf/m/{0}.deleted'.format(unicode(uuid))

def filename_for_route_markup(route):
    return 'wf/r/{0}.{1}.bpml'.format(route.name,
                                       route.version)

def filename_for_deleted_route_markup(route):
    timestamp = datetime.datetime.now().strftime('%s')
    return 'wf/r/{0}.{1}.deleted.bpml'.format(route.name,
                                               timestamp)

def filename_for_process_markup(process):
    return 'wf/p/{0}.bpml'.format(process.object_id)

def filename_for_deleted_process_markup(process):
    return 'wf/p/{0}.deleted.bpml'.format(process.object_id)


def filename_for_process_code(process):
    return 'wf/p/{0}.{1}.cpm'.format(process.object_id, process.version)

def filename_for_versioned_process_code(pid, vid):
    return 'wf/p/{0}.{1}.cpm'.format(pid, vid)

#
# Process log caching
#

def filename_for_process_log(object_id, version):
    return 'cache/oie/processlog/{0}.{1}.log'.format(object_id, version)

def read_cached_process_log(object_id, version):
    handle = BLOBManager.Open(filename_for_process_log(object_id, version), 'r')
    if (handle is None):
        return None
    log_text = handle.read()
    BLOBManager.Close(handle)
    return log_text

def delete_cached_process_logs(object_id):
    # TODO: Implement
    return
    #cached_vevents = BLOBManager.List('cache/vevent')
    #for file in cached_vevents:
    #    BLOBManager.Delete('cache/vevent/' + file)

def cache_process_log(object_id, version, log_text):
    # TODO: Is this concurrent safe?  We should apply a lock.
    delete_cached_process_logs(object_id)
    filename = filename_for_process_log(object_id, version)
    handle = BLOBManager.Create(filename.split('/'))
    handle.write(log_text)
    handle.flush()
    BLOBManager.Close(handle)

#
# Process VEVENT caching
#

def filename_for_vevent(object_id, version):
    return 'cache/vevent/{0}.{1}.ics'.format(object_id, version)

def is_vevent_cached(object_id, version):
    return BLOBManager.Exists(filename_for_vevent(object_id, version))

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


def parse_property_encoded_acl_list(value):
    # TEST: CoilsLogicWorkflowParseACLProperyString

    if not isinstance(value, basestring):
        return [ ]

    BLANK_ACL = [ '', 'allowed', '' ]
    PARSER_MODE_CONTEXT     = 0
    PARSER_MODE_PERMISSIONS = 2
    acls = [ ]
    acl  = deepcopy(BLANK_ACL)
    CURRENT_PARSER_MODE = PARSER_MODE_CONTEXT

    for c in value:
        if c.isdigit() and CURRENT_PARSER_MODE == PARSER_MODE_CONTEXT:
            acl[0] = '{0}{1}'.format(acl[0], c)
        elif c.isalpha() and CURRENT_PARSER_MODE == PARSER_MODE_PERMISSIONS:
            acl[2] = '{0}{1}'.format(acl[2], c)
        elif c == ';':
            CURRENT_PARSER_MODE = PARSER_MODE_CONTEXT
            acls.append(acl)
            acl = deepcopy(BLANK_ACL)
        elif c in ('+', '-') and CURRENT_PARSER_MODE == PARSER_MODE_CONTEXT:
            if c == '-': acl[1] = 'denied'
            CURRENT_PARSER_MODE = PARSER_MODE_PERMISSIONS
        else:
            raise CoilsException('Unable to parse {http://www.opengroupware.us/}defaultProcessACLs')

    return acls
