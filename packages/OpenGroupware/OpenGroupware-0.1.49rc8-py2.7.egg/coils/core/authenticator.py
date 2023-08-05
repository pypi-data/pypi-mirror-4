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
import logging
from exception import CoilsException, AuthenticationException
from coils.foundation import *
from sqlalchemy import *

class Authenticator(object):
    # TODO: Support some reasonable kind of cache (a class cache is worthless)
    _hosts = None
    _debug = None

    def __init__(self, context, metadata, options):
        self.log = logging.getLogger('authenticator')
        self.account = None
        self.set_context(context)
        self.set_metadata(metadata)
        self.set_options(options)
        if (self.login is not None):
            self.log.debug('login detected, trying authentication')
            if (self.options.get('stripDomain', False)):
                self.set_login(self.login.split('\\')[-1:][0])
            # Issue#102 : Support for the LSUseLowercaseLogin default
            if (self.options.get('lowerLogin', False)):
                self.set_login(self.login.lower())
            # Issue#101: Support "AllowSpacesInLogin" default
            if (self.options.get('allowSpaces', False)):
                pass
            else:
                self.set_login(self.login.replace(' ', ''))
        # Call the authenticate method
        if (self.login is not None):
            self.authenticate()
        else:
            self.log.debug('No credentials, not attempting authentication')
            raise AuthenticationException('No credentials, not attempting authentication')

    @property
    def debugging_enabled(self):
        if (Authenticator._debug is None):
            if (ServerDefaultsManager().bool_for_default('LSAuthDebugEnabled')):
                Authenticator._debug = True
            else:
                Authenticator._debug = False
        return Authenticator._debug

    def set_context(self, context):
        self._context = context

    @property
    def context(self):
        return self._context

    def set_options(self, options):
        self._options = options

    @property
    def options(self):
        return self._options

    def set_metadata(self, metadata):
        self._metadata = metadata

    @property
    def metadata(self):
        return self._metadata

    @property
    def login(self):
        return self.metadata['authentication'].get('login', None)

    def set_login(self, login):
        self._metadata['authentication']['login'] = login

    @property
    def secret(self):
        return self.metadata['authentication'].get('secret', None)

    def authenticate(self):
        ''' Perform token based authentication that should ALWAYS work
            regardless of identification/authentication backend.
            TODO: Implement token based authentication, see OGo/J '''
        # NOTE: This is the method that child classes want to override
        # WARN: Currently we only support BASIC (aka PLAIN), but someday....
        if (self._check_tokens()): return True
        if (self._check_trusted_hosts()): return True
        self.account = self.get_login()
        return False

    def _check_tokens(self):
        # TODO: Implement
        # How does OGo/J do this?
        if (self.debugging_enabled):
            self.log.warn("Tokens authentication not implemented.")
        return False

    def _check_trusted_hosts(self):
        if ('connection' in self.metadata):
            if (self.debugging_enabled):
                self.log.debug('Checking Trusted Host authentication.')
            # Context is for a network connected client
            connection = self.metadata.get('connection')
            if (self.debugging_enabled):
                self.log.debug('Client connection from {0}'.format(connection.get('client_address')))
            if ((connection.get('client_address').lower() in self.options.get('trustedHosts', [])) and
                ('claimstobe' in self.metadata['authentication'])):
                self.set_login(self.metadata['authentication']['claimstobe'])
                self.account = self.get_login()
                self.log.info('Trusted Host authentication as "{0}" (objectId#{1}) from remote "{2}" approved.'.format(
                    self.account.login,
                    self.account.object_id,
                    connection.get('client_address')))
                return True
            else:
                if (self.debugging_enabled):
                    self.log.debug('Trusted Host autentication denied from {0}'.format(
                        connection.get('client_address')))
        return False

    def get_login(self):
        # TODO: Can we do something short of loading the entire contact entity?
        if (self.debugging_enabled):
            self.log.debug('Checking database for login "{0}".'.format(self.login))
        db = self.context.db_session()
        query = db.query(Contact).filter(and_(Contact.login==self.login,
                                               Contact.is_account==1,
                                               Contact.status!='archived'))
        data = query.all()
        if (len(data) > 1):
            self.log.error('Multiple accounts match login {0); database integrity suspect.'.format(self.login))
            raise AuthenticationException('Multiple accounts match login; database integrity suspect.')
        elif (len(data) == 0):
            if (self.debugging_enabled):
                self.log.debug('No such account as {0}.'.format(self.login))
            result = self.provision_login()
            if (result is None):
                if (self.debugging_enabled):
                    self.log.debug('Unable to auto-provision for login {0}.'.format(self.login))
                raise AuthenticationException('No such account as {0}.'.format(self.login))
            return result
        elif (len(data) == 1):
            if (self.debugging_enabled):
                self.log.debug('Found account for login "{0}".'.format(self.login))
            return data[0]
        else:
            raise AuthenticationException('Undefined authentication error - contact developers.')

    def provision_login(self):
        ''' Authenticators can override this method to support auto-provisioning of
            user accounts.  If the account cannot be auto-provsioned this method
            should return None; if the authenticator does not support provisioning
            just return None. '''
        return None

    def authenticated_id(self):
        if (self.account is not None):
            return self.account.object_id
        return -1

    def authenticated_login(self):
        if (self.account is not None):
            return self.account.login
        return None
