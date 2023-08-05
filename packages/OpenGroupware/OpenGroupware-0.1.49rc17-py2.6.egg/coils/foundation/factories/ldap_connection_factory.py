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
import logging
from coils.foundation.defaultsmanager import ServerDefaultsManager
try:
    import ldap, ldap.sasl
except:
    class LDAPConnectionFactory(object):

        @staticmethod
        def Connect(source):
            raise Exception('LDAP support not available')
else:
    class LDAPConnectionFactory(object):
        _dits = None
    
        @staticmethod
        def Connect(source):
            log = logging.getLogger('OIE')
            sd = ServerDefaultsManager()
            config = sd.default_as_dict('OIELDAPSources')
            if (source in config):
                config = config.get(source)
                try:
                    dsa = ldap.initialize(config.get('url'))
                    if (config.get('starttls', 'YES').upper() == 'YES'):
                        dsa.start_tls_s()
                    if (config.get('bindmech', 'SIMPLE').upper() == 'SIMPLE'):
                        dsa.simple_bind_s(config.get('identity'),
                                          config.get('secret'))
                    else:
                        raise NotImplementedException('Non-simple LDAP bind not implemented')
                        tokens = ldap.sasl.digest_md5(config.get('identity'),
                                                      config.get('secret'))
                        dsa.sasl_interactive_bind_s("", tokens)
                except Exception, e:
                    log.exception(e)
                    log.error('Unable to provide connection to source name {0}'.format(source))
                    return None
                else:
                    return dsa
            else:
                log.error('No LDAP source defined with name {0}'.format(source))
                return None


