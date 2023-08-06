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
from coils.core              import *
from coils.foundation        import ldap_paged_search
from coils.core.logic        import ActionCommand
from dsml1_writer            import DSML1Writer

try:
    import ldap
except:
    class SearchAction(object):
        pass
else:
    class SearchAction(ActionCommand):
        # TODO: Make page size a default (low priority) Issue#92
        # TODO: Support "base" and "one" scopes. Issue#91
        __domain__    = "action"
        __operation__ = "ldap-search"
        __aliases__   = [ 'ldapSearch', 'ldapSearchAction' ]
        __debugOn__   = None
    
        def __init__(self):
            ActionCommand.__init__(self)
            if (SearchAction.__debugOn__ is None):
                sd = ServerDefaultsManager()
                SearchAction.__debugOn__ = sd.bool_for_default('LDAPDebugEnabled')
    
        @property
        def debugOn(self):
            return SearchAction.__debugOn__
    
        def do_action(self):
            dsa = LDAPConnectionFactory.Connect(self._dsa)
            if (dsa is None):
                raise CoilsException('Unable to acquire connection to DSA "{0}"'.format(self._dsa))
            if (self.debugOn): self.log.debug('LDAP SEARCH: Got connection to DSA')
            if (len(self._xattrs) == 0):
                self.xattrs = None
            try:
                results = ldap_paged_search( connection    = dsa,
                                             logger        = self.log,
                                             search_filter = self._xfilter,
                                             search_base   = self._xroot,
                                             attributes    = self._xattrs,
                                             search_scope  = self._xscope )
            except ldap.NO_SUCH_OBJECT, e:
                self.log.exception(e)
                self.log.info('LDAP NO_SUCH_OBJECT exception, generating empty message')
            except ldap.INSUFFICIENT_ACCESS, e:
                self.log.exception(e)
                self.log.info('LDAP INSUFFICIENT_ACCESS exception, generating empty message')
            except ldap.SERVER_DOWN, e:
                self.log.exception(e)
                self.log.warn('Unable to contact LDAP server!')
                raise e
            except Exception, e:
                self.log.error('Exception in action ldapSearch')
                self.log.exception(e)
                raise e
            else:
                if (self.debugOn): self.log.debug('LDAP SEARCH: Formatting results to DSML.')
                writer = DSML1Writer()
                writer.write(results, self.wfile)
            dsa.unbind()
    
        def parse_action_parameters(self):
            self._dsa     = self.action_parameters.get('dsaName',     None)
            self._xfilter = self.action_parameters.get('filterText',  None)
            self._xroot   = self.action_parameters.get('searchRoot',  None)
            self._xscope  = self.action_parameters.get('searchScope', 'SUBTREE').upper()
            self._xlimit  = int(self.action_parameters.get('searchLimit', 150))
            self._xattrs = []
            
            for xattr in self.action_parameters.get('attributes', '').split(','):
                self._xattrs.append(str(xattr))
                
            if (self._dsa is None):
                raise CoilsException('No DSA defined for ldapSearch')
                
            # Check query value
            if (self._xfilter is None):
                raise CoilsException('No filter defined for ldapSearch')
            else:
                self._xfilter = self.decode_text(self._xfilter)
                self._xfilter = self.process_label_substitutions(self._xfilter)
                #self.log.info('LDAP Filter Text: {0}'.format(self._xfilter))
                
            # Check root parameter
            if (self._xroot is None):
                raise CoilsException('No root defined for ldapSearch')
            else:
                self._xroot = self.decode_text(self._xroot)
                
            # Convert subtree parameter
            if (self._xscope == 'SUBTREE'):
                self._xscope = ldap.SCOPE_SUBTREE
            else:
                self._xscope = ldap.SCOPE_SUBTREE
                
            if (self.debugOn):
                self.log.debug('LDAP SEARCH FILTER:{0}'.format(self._xfilter))
                self.log.debug('LDAP SEARCH BASE:{0}'.format(self._xroot))
                self.log.debug('LDAP SEARCH LIMIT:{0}'.format(self._xlimit))
    
        def do_epilogue(self):
            pass
