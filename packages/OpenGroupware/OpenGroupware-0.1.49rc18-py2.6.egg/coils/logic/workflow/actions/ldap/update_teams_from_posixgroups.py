#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core          import CoilsException
from coils.foundation    import ldap_paged_search, LDAPConnectionFactory
from coils.core.logic    import ActionCommand

try:
    import ldap
except:
    class UpdateTeamsFromPOSIXGroups(object):
        pass
else:
    class UpdateTeamsFromPOSIXGroups(ActionCommand):
        __domain__ = "action"
        __operation__ = "update-teams-from-posix-groups"
        __aliases__   = [ 'updateTeamsFromPOSIXGroups', "updateTeamsFromPOSIXGroupsAction" ]
    
        def __init__(self):
            ActionCommand.__init__(self)

        @property
        def result_mimetype(self):
            return 'text/plain'

        def do_action(self):

            if self._xscope == 'ONELEVEL':
                self._xscope = ldap.SCOPE_ONELEVEL
            else:
                self._xscope = ldap.SCOPE_SUBTREE

            if (self._ctx.is_admin):

                dsa = LDAPConnectionFactory.Connect(self._dsa)

                results = ldap_paged_search(connection    = dsa,
                                            logger        = self.log,
                                            search_filter = self._xfilter,
                                            search_base   = self._xroot,
                                            attributes    = ['opengroupwareid','memberuid'],
                                            search_scope  = self._xscope)

                count = 0
                for group in results:
                    count += 1
                    ldap_dn     = group[0]
                    member_uids = group[1]['memberUid']
                    team_id     = group[1]['opengroupwareid'][0]
                
                    self.wfile.write('\n'.format(team_id))
                    team = self._ctx.run_command('team::get', id=team_id)
                    member_ids = [ ]
                    self.wfile.write('LDAP DN:{0}\n'.format(ldap_dn))
                    if team:
                        self.wfile.write('Performing membership sync of teamId#{0}:"{1}"\n'.format(team_id, team.name))
                        for uid in member_uids:
                            account = self._ctx.run_command('account::get', login=uid)
                            if account:
                                member_ids.append(account.object_id)
                            else:
                                self.wfile.write('  Unable to find account object for uid "{0}"\n'.format(uid))
                        self.wfile.write('  Assigning {0} members for {1} uids.\n'.format(len(member_ids), len(member_uids)))
                        self._ctx.run_command('team::set', object=team, values={'memberObjectIds': member_ids})
                    else:
                        self.wfile.write('Unable to find team object for id#{0}\n'.format(team_id))
                
                self.wfile.write('\n')
                self.wfile.write('Synchronized the membership of {0} groups'.format(count));
            else:
                raise CoilsException('Insufficient privilages to invoke {0}'.format(self.__operation__))

        def parse_action_parameters(self):
                self._dsa     = self.action_parameters.get('dsaName',     None)
                self._xfilter = self.action_parameters.get('filterText',  None)
                self._xroot   = self.action_parameters.get('searchRoot',  None)
                self._xscope  = self.action_parameters.get('searchScope', 'SUBTREE').upper()
