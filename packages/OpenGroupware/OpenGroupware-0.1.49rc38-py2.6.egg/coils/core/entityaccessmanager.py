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
# THE SOFTWARE.
#
import time, logging
from sqlalchemy  import *
from exception   import *
from coils.foundation import *

# Permissions; we use the same flags as IMAP except "v"
#  r = read
#  w = write (modify)
#  l = list
#  d = delete [synonymous with t + x]
#  a = administer
#  k = create [not implemented]
#  t = delete object
#  x = delete container [not implemented]
#  i = insert [not implemented]
#  v = view [?]

COILS_CORE_FULL_PERMISSIONS=['r', 'w', 'l', 'd', 'a',
                             'k', 't', 'x', 'i', 'v']

class EntityAccessManager(object):
    """ Calculate the access to an entity in the current context.
        There is no single point of the code more performance critical than
        this object.  The server actually spends most of its time
        right here.
    """
    __DebugOn__ = None

    def __init__(self, ctx):
        if (hasattr(self, '__entity__')):
            if (isinstance(self.__entity__, list)):
                name = ''
                for e in self.__entity__:
                    if (len(name) > 0):
                        name = '%s-%s' % (name, e.lower())
                    else:
                        name = e.lower()
            else:
                name = self.__entity__.lower()
            self.log = logging.getLogger('access.%s' % name)
        else:
            self.log = logging.getLogger('entityaccessmanager')
            self.log.warn('{0} has not __entity__ attribute'.format(repr(self)))
        if (EntityAccessManager.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            EntityAccessManager.__DebugOn__ = sd.bool_for_default('OGoAccessManagerDebugEnabled')
        self._ctx = ctx

    @property
    def debug(self):
        return  EntityAccessManager.__DebugOn__

    def materialize_rights(self, **params):

        if (params.has_key('objects')):
            objects = params['objects']
        else:
            return { }

        if (params.get('contexts', None) is not None):
            self.context_ids = params.get('contexts')
        else:
            if self._ctx.is_admin:
                if self.debug:
                    self.log.debug('administrative account has all rights to all objects if no contexts are specified')
                rights = { }
                for entity in objects:
                    rights[entity] = set()
                    for right in list('lrwadv'):
                        rights[entity].add(right)
                return rights
            else:
                self.context_ids = self._ctx.context_ids

        start = time.time()
        rights = self.implied_rights(objects)
        if (self.debug):
            self.log.debug('duration of implied rights was %0.3f' % (time.time() - start))
        start = time.time()
        rights = self.asserted_rights(rights)
        if (self.debug):
            self.log.debug('duration of asserted rights was %0.3f' % (time.time() - start))
        start = time.time()
        rights = self.revoked_rights(rights)
        if (self.debug):
            self.log.debug('duration of revoked rights was %0.3f' % (time.time() - start))
        return rights

    def default_rights(self):
        return COILS_CORE_FULL_PERMISSIONS

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
        return rights

    def asserted_rights(self, object_rights):
        for entity in object_rights.keys():
            if (hasattr(entity, 'acls')):
                rights = object_rights[entity]
                permissions = set(list(self.get_acls('allowed', entity)))
                for right in permissions:
                    rights.add(right)
                object_rights[entity] = rights
        return object_rights

    def revoked_rights(self, object_rights):
        for entity in object_rights.keys():
            if (hasattr(entity, 'acls')):
                asserted = object_rights[entity]
                denied = self.get_acls('denied', entity)
                object_rights[entity] = asserted.difference(denied)
        return object_rights

    def get_acls(self, action, entity):
        rights = set()
        counter = 0
        for acl in entity.acls:
            if (acl.action == action):
                counter = counter + 1
                if (acl.context_id in self.context_ids):
                    permissions = set(list(acl.permissions))
                    if (permissions.issubset(rights)):
                        continue
                    for right in permissions:
                        rights.add(right)
        return rights

    @staticmethod
    def List(ctx, properties):
        raise NotImplementedException('EntityAccessManager does not implement List')

    @staticmethod
    def ListSubquery(ctx, contexts=None, mask='r'):
        raise NotImplementedException('EntityAccessManager does not implement ListSubquery')
