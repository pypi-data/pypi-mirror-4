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
# T
import os, pwd, grp, string

# Issue#93 0x1F is no stripped by the MS_TRANSCODE_TABLE
MS_TRANSCODE_TABLE = string.maketrans(#Input
                         # Control Characters
                         #\U0000 to \U001F, \U007F, and from \U0080 to \U009F
                         chr(0x19) + 
                         chr(0x1c) + chr(0x1d) + chr(0x1e) + chr(0x1f) +
                         chr(0x85) +
                         chr(0x91) + chr(0x92) + chr(0x93) + chr(0x94) +
                         chr(0x95) + chr(0x96) + chr(0x97) + chr(0x98) +
                         chr(0x99) +
                         # A - Graphics Characters
                         chr(0xa1) + chr(0xa2) + chr(0xa3) + chr(0xa4) +
                         chr(0xa5) + chr(0xa6) + chr(0xa7) + chr(0xa8) +
                         chr(0xa9) + chr(0xaa) + chr(0xab) + chr(0xac) +
                         chr(0xad) + chr(0xae) + chr(0xaf) +
                         # B - Block Characters
                         chr(0xb1) + chr(0xb2) + chr(0xb3) + chr(0xb4) +
                         chr(0xb5) + chr(0xb6) + chr(0xb7) + chr(0xb8) +
                         chr(0xb9) + chr(0xba) + chr(0xbb) + chr(0xbc) +
                         chr(0xbd) + chr(0xbe) + chr(0xbf) +
                         # C - Block Characters
                         chr(0xc1) + chr(0xc2) + chr(0xc3) + chr(0xc4) +
                         chr(0xc5) + chr(0xc6) + chr(0xc7) + chr(0xc8) +
                         chr(0xc9) + chr(0xca) + chr(0xcb) + chr(0xcc) +
                         chr(0xcd) + chr(0xce) + chr(0xcf) +
                         # D - Block Characters
                         chr(0xd1) + chr(0xd2) + chr(0xd3) + chr(0xd4) +
                         chr(0xd5) + chr(0xd6) + chr(0xd7) + chr(0xd8) +
                         chr(0xd9) + chr(0xda) + chr(0xdb) + chr(0xdc) +
                         chr(0xdd) + chr(0xde) + chr(0xdf) +
                         # E - Math Characters
                         chr(0xe1) + chr(0xe2) + chr(0xe3) + chr(0xe4) +
                         chr(0xe5) + chr(0xe6) + chr(0xe7) + chr(0xe8) +
                         chr(0xe9) + chr(0xea) + chr(0xeb) + chr(0xec) +
                         chr(0xed) + chr(0xee) + chr(0xef) +
                         # F - Math Characters
                         chr(0xf1) + chr(0xf2) + chr(0xf3) + chr(0xf4) +
                         chr(0xf5) + chr(0xf6) + chr(0xf7) + chr(0xf8) +
                         chr(0xf9) + chr(0xfa) + chr(0xfb) + chr(0xfc) +
                         chr(0xfd) + chr(0xfe) + chr(0xff),
                         #Output
                         chr(0x27) + 
                         chr(0x22) + chr(0x22) + chr(0x63) + chr(0x20) +
                         chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x2d) + 
                         # A - Graphics Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) +
                         # B - Block Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) +
                         # C - Block Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + 
                         # D - Block Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) +
                         # E - Math Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) +
                         # F - Math Characters
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) + 
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63) + chr(0x63) +
                         chr(0x63) + chr(0x63) + chr(0x63))

def diff_id_lists(inbound, present):
    rm = []
    add = []
    for id in inbound:
        if (id not in present):
            add.append(id)
    for id in present:
        if (id not in inbound):
            rm.append(id)
    return (add, rm)

def change_to_backend_usergroup(user, group):
    uid = pwd.getpwnam(user).pw_uid
    gid = grp.getgrnam(group).gr_gid
    os.setreuid(uid, uid)

def fix_microsoft_text(text):
    # Translate tables don't work for Unicode, so we need to make sure this
    # function gets a str type, not unicode - or else it fails. Developer
    # need to be careful about when they use this.
    return str(text).translate(MS_TRANSCODE_TABLE)

def get_server_root( store_root = None ):
    # We need to find & set the server's document root
    # Order is (1) Was a "store_root" specified in params
    #          (2) Is the OGO_SERVER_ROOT environment variable set
    #          (3) Default to "/var/lib/opengroupware.org"
    if not store_root:
        store_root = os.getenv('OGO_SERVER_ROOT', None)
    if not store_root:
        # TODO: We should possibly complain to the  admin
        store_root = '/var/lib/opengroupware.org'         
    print("Store root is {0}".format(store_root))
    return store_root

try:
    import ldap
except:
    def ldap_paged_search(connection, search_base, search_filter, attributes, scope=None, logger=None):
        raise Exception('LDAP Searches not supported on this instance; missing dependency')
else:
    def ldap_paged_search(connection, search_base, search_filter, attributes,
                          search_scope = ldap.SCOPE_SUBTREE,
                          logger = None):

        if not connection:
            raise Exception('No LDAP connection available.')

        # Test for Python-LDAP version;  at version 2.4.0 they restructured
        # how server controls were managed - each control is now an object.     
        PYTHON_LDAP_24 = hasattr(ldap, 'CONTROL_PAGEDRESULTS')

        if PYTHON_LDAP_24:
            control = ldap.controls.SimplePagedResultsControl(size=128, cookie='')
        else:
            control = ldap.controls.SimplePagedResultsControl(ldap.LDAP_CONTROL_PAGE_OID, True, (128, ''))
            
        if logger:
            logger.debug('LDAP Filter: {0}'.format(search_filter))
            logger.debug('LDAP Base: {0}'.format(search_base))
            logger.debug('LDAP Attributes: {0}'.format(attributes))

        if PYTHON_LDAP_24:
            message_id = connection.search_ext(search_base,
                                               scope=search_scope,
                                               filterstr=search_filter,
                                               attrlist=attributes,
                                               attrsonly=0,
                                               timeout=-1,
                                               serverctrls=[control])
        else:
            message_id = connection.search_ext(search_base,
                                               search_scope,
                                               search_filter,
                                               attrlist=attributes,
                                               serverctrls=[control])
                                           
        if logger:
            logger.debug('initial ldap search executed')
        results = []
        page = 0
        while True:
            
            page += 1
            
            if logger:
                logger.debug('requesting result page {0}'.format(page))
                
            rtype, rdata, rmsgid, serverctrls = connection.result3(message_id)
            
            results.extend(rdata)
            
            if logger:
                logger.debug('retrieved results for page {0}; total'.format(page, len(results)))
            
            if PYTHON_LDAP_24:
                
                # Pages result retrieval using Python-LDAP 2.4.0 and later
                pctrls = [ c for c in serverctrls if isinstance(c, ldap.controls.SimplePagedResultsControl) ]
                if pctrls:
                    est = pctrls[0].size
                    cookie = pctrls[0].cookie
                    if cookie:
                        control.cookie = cookie
                        message_id = connection.search_ext(search_base,
                                                           scope=search_scope,
                                                           filterstr=search_filter,
                                                           attrlist=attributes,
                                                           serverctrls=[control])         
                    else:
                        break
                else:
                    raise Exception('Failure to apply LDAP pages results control.')
                    
            else:
                # Pages result retrieval using Python-LDAP earlier than 2.4.0
                pctrls = [ c for c in serverctrls if c.controlType == ldap.LDAP_CONTROL_PAGE_OID ]
                if pctrls:
                    est, cookie = pctrls[0].controlValue
                    if cookie:
                        control.controlValue = (10, cookie)
                        message_id = connection.search_ext(search_base,
                                                           search_scope,
                                                           search_filter,
                                                           attrlist=attributes,
                                                           serverctrls=[control])
                    else:
                        break
                else:
                    raise Exception('Failure to apply LDAP pages results control.')

        return results
