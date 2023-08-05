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
from authenticator    import Authenticator
from exception        import CoilsException, AuthenticationException
from coils.foundation import Session, Contact, ServerDefaultsManager

try:
    import ldap, ldap.sasl
except:
    class LDAPAuthenticator(Authenticator):
        def __init__(self, context, metadata, options):
            raise Exception('LDAP support not available')
else:
    import ldaphelper

    class LDAPAuthenticator(Authenticator):
        _dsa        = None
        _ldap_debug = None

        def __init__(self, context, metadata, options):
            self._verify_options(options)
            Authenticator.__init__(self, context, metadata, options)

        @property
        def ldap_debug_enabled(self):
            if (LDAPAuthenticator._ldap_debug is None):
                if (ServerDefaultsManager().bool_for_default('LDAPDebugEnabled')):
                    LDAPAuthenticator._ldap_debug = True
                else:
                    LDAPAuthenticator._ldap_debug = False
            return LDAPAuthenticator._ldap_debug

        def _verify_options(self, options):
            #TODO: Check the options to make sure we have function values
            return
    
        def _bind_and_search(self, options, login):
            # Bind to the DSA and search for the user's DN
            dsa = ldap.initialize(options['url'])
            if (options['start_tls'] == 'YES'):
                if (self.ldap_debug_enabled):
                    self.log.debug('Starting TLS')
                dsa.start_tls_s()
            if (options['binding'] == 'SIMPLE'):
                dsa.simple_bind_s(options['bind_identity'],
                                  options['bind_secret'])
                if (self.ldap_debug_enabled):
                    self.log.debug('Starting TLS')                                  
            elif (options['binding'] == 'DIGEST'):
                tokens = ldap.sasl.digest_md5(options['bind_identity'],
                                              options['bind_secret'])
                dsa.sasl_interactive_bind_s("", tokens)
                self._search_bind()
            search_filter = options["search_filter"]
            if (search_filter is None):
                search_filter = '({0}=%s)'.format(options["uid_attribute"]) % login
                if (self.ldap_debug_enabled):
                    self.log.error('No LDAP filter configured, defaulting to "{0}"'.format(search_filter))
            else:
                search_filter = search_filter % login
            if (self.ldap_debug_enabled):
                self.log.debug('LDAP Container: {0}'.format(options["search_container"]))
                self.log.debug('LDAP Filter: {0}'.format(search_filter))
                self.log.debug('LDAP UID Attribute: {0}'.format(options["uid_attribute"]))
            result = dsa.search_s(options["search_container"],
                                  ldap.SCOPE_SUBTREE,
                                  search_filter,
                                  [ options["uid_attribute"] ])
            result = ldaphelper.get_search_results( result )
            if (self.ldap_debug_enabled):
                self.log.debug('Found {0} results.'.format(len(result)))
            return result

        def _test_simple_bind(self, options, dn, secret):
            dsa = ldap.initialize(options['url'])
            if (options['start_tls'] == 'YES'):
                LDAPAuthenticator._dsa.start_tls_s()
            result = False
            try:
                dsa.simple_bind_s(dn, secret)
                result = True
                dsa.unbind()
            except Exception, e:
                self.log.exception(e)
            return result

        def _get_ldap_object(self):
            if (self.options['binding'] == 'SIMPLE'):
                accounts = self._bind_and_search(self.options, self.login)
                if (len(accounts) == 0):
                    raise AuthenticationException('Matching account not returned by DSA')
                elif (len(accounts) > 1):
                    raise AuthenticationException('Dupllicate accounts returned by DSA')
                else:
                    # Only one found
                    dn = accounts[0].get_dn()
                    if (self.ldap_debug_enabled):
                        self.log.debug('Testing authentication bind as {0}'.format(dn))
                    if (dn is None):
                        self.log.warn('LDAP object with null DN!')
                if (self._test_simple_bind(self.options, dn, self.secret)):
                    self.log.debug('LDAP bind with {0}'.format(dn))
                    return accounts[0]
                else:
                    raise AuthenticationException('DSA declined username or password')
            elif (self.options['binding'] == 'SASL'):
                # TODO Implement LDAP SASL bind test
                raise AuthenticationException('SASL bind test not implemented!')

        def authenticate(self):
            if (Authenticator.authenticate(self)):
                return True
            ldap_object = self._get_ldap_object()
            if (ldap_object is not None):
                return True
            raise AuthenticationException('Incorrect username or password')

        def provision_login(self):
            ''' Authenticators can override this method to support auto-provisioning of
                user accounts.  If the account cannot be auto-provsioned this method
                should return None; if the authenticator does not support provisioning
                just return None. '''
            ldap_object = self._get_ldap_object()                
            return None