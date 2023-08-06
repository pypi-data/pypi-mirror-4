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
import json
from coils.core          import CoilsException, PropertyManager
from coils.foundation    import ldap_paged_search, LDAPConnectionFactory
from coils.core.logic    import ActionCommand

try:
    import ldap
except:
    class FillLDAPMailRoutingAction(object):
        pass
else:
    class FillLDAPMailRoutingAction(ActionCommand):
        __domain__ = "action"
        __operation__ = "fill-ldap-mail-routing"
        __aliases__   = [ 'fillLDAPMailRouting', "fillLDAPMailRoutingAction" ]

        def __init__(self):
            ActionCommand.__init__(self)

        @property
        def result_mimetype(self):
            return 'text/plain'

        def do_action(self):

            if not self._ctx.is_admin:
                raise CoilsException('Insufficient privilages to invoke {0}'.format(self.__operation__))

            dsa = LDAPConnectionFactory.Connect(self._dsa)

            if not dsa:
                raise CoilsException('No LDAP/DSA connection available to DSA {0}'.format(self._dsa))

            # HACK: python-ldap does not like unicode attribute names
            #       hence - [str(x) for x in self._xmap.keys()]
            # WARN: This probably breaks in Python 3!
            attributes = [ ]
            if self._xuid1: attributes.append(self._xuid1)
            if self._xuid2: attributes.append(self._xuid2)
            if self._gn_attr: attributes.append(self._gn_attr)
            if self._mn_attr: attributes.append(self._sn_attr)
            if self._sn_attr: attributes.append(self._mn_attr)
            if self._mail_attr: attributes.append(self._mail_attr)
            attributes = [str(x) for x in attributes]

            results = ldap_paged_search(connection    = dsa,
                                        logger        = self.log,
                                        search_filter = self._xfilter,
                                        search_base   = self._xroot,
                                        attributes    = attributes,
                                        search_scope  = self._xscope)

            self.wfile.write('LDAP Filter:{0}\n'.format(self._xfilter))
            self.wfile.write('LDAP Base:{0}\n'.format(self._xroot))
            self.wfile.write('LDAP Attributes:{0}\n'.format(attributes))
            self.wfile.write('\n')
            self.wfile.write('Search found {0} results\n'.format(len(results)))
            self.wfile.write('\n')

            all_addresses = [ ]

            count = 0
            for user in results:

                #import pprint
                #self.log.info(user)
                #self.wfile.write(pprint.pformat(user)
                self.wfile.write('LDAP DN:{0}\n'.format(user[0]))

                count += 1

                mn = None

                if ((self._gn_attr in user[1]) and
                   (self._mn_attr in user[1]) and
                   (self._sn_attr in user[1])):
                    mn = user[1][self._mn_attr][0]
                    self.wfile.write('  *  Middle name is: "{0}"'.format(mn))
                    if self._mn_is_initials:
                        if len(mn) == 3:
                            mn = mn[1:2]
                        else:
                            mn = None
                    else:
                        mn = user[1][self._mn_attr][0]

                if mn:
                    vanity = '{0}.{1}.{2}'.format(user[1][self._gn_attr][0].lower(),
                                                  mn.lower(),
                                                  user[1][self._sn_attr][0].lower())
                    self.wfile.write('  * Vanity address: {0}\n'.format(vanity))
                else:
                    self.wfile.write('  * No vanity address constructed\n')
                    vanity = None

                addresses = [ ]
                for domain in self._domains:
                    addresses.append('{0}@{1}'.format(user[1][self._xuid1][0], domain))
                    if self._xuid2 in user[1]:
                        for uid_alias in user[1][self._xuid2]:
                            addresses.append('{0}@{1}'.format(uid_alias, domain))
                    if vanity:
                        addresses.append('{0}@{1}'.format(vanity, domain))

                modifications = [ ]
                if self._mail_attr in user[1]:
                    existing_addresses = user[1][self._mail_attr]
                else:
                    existing_addresses = [ ]
                for address in existing_addresses:
                    if address not in addresses:
                        self.wfile.write('  Removing {0}\n'.format(address))
                        modifications.append( ( ldap.MOD_DELETE, self._mail_attr, address, ) )
                for address in addresses:
                    if address not in existing_addresses:
                        self.wfile.write('  Adding {0}\n'.format(address))
                        modifications.append( ( ldap.MOD_ADD, self._mail_attr, address, ) )

                if modifications:
                    dsa.modify_s(user[0], modifications)
                    self.wfile.write('  = Performing modifications.\n')
                else:
                    self.wfile.write('No modifications required.\n'.format(user[0]))

                self.wfile.write('\n')

        def parse_action_parameters(self):
                self._dsa     = self.action_parameters.get('dsaName',     None)
                self._xfilter = self.action_parameters.get('filterText',  None)
                self._xroot   = self.action_parameters.get('searchRoot', 'SUBTREE').upper()
                self._xscope  = self.action_parameters.get('searchScope', 'SUBTREE').upper()
                # Attributes
                self._domains = self.action_parameters.get('mailDomains',  None)
                self._xuid1   = self.action_parameters.get('uidAttribute1',  'uid')
                self._xuid2   = self.action_parameters.get('uidAttribute2',  None)
                # Attributes for building long-vanity e-mail aliases like adam.t.williams@example.com
                self._gn_attr = self.action_parameters.get('gnAttribute',  None)
                self._sn_attr = self.action_parameters.get('snAttribute',  None)
                self._mn_attr = self.action_parameters.get('mnAttribute',  None)
                self._mn_is_initials = self.action_parameters.get('mnIsInitials',  'NO')
                self._mail_attr  = self.action_parameters.get('mailAddressAttribute', 'mailLocalAddress')

                self._domains = [x.strip() for x in self._domains.split(',')]

                if self._mn_is_initials.upper() == 'YES':
                    self._mn_is_initials = True
                else:
                    self._mn_is_initials = False



                if not self._dsa:
                    raise CoilsException('No dsaNAME parameter specified for fillLDAPMailRoutingAction')

                if not self._xfilter:
                    raise CoilsException('No filterText [LDAP Search Filter] parameter specified for fillLDAPMailRoutingAction')


                if not self._xroot:
                    raise CoilsException('No searchRoot parameter specified for fillLDAPMailRoutingAction')

                if self._xscope == 'ONELEVEL':
                    self._xscope = ldap.SCOPE_ONELEVEL
                else:
                    self._xscope = ldap.SCOPE_SUBTREE
