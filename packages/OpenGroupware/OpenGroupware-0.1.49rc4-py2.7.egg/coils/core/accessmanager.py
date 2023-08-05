#
# Copyright (c) 2009, 2011, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import os, sys, glob, inspect, time, logging
try:
  from coils.foundation import *
except ImportError:
  print 'Coils Model package not found, required by Coils Core!'
  sys.exit(2)
from entityaccessmanager import EntityAccessManager
from bundlemanager       import BundleManager

class AccessManager:
    __DebugOn__     = None

    def __init__(self, ctx):
        self.log = logging.getLogger('accessmanager')
        if (AccessManager.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            AccessManager.__DebugOn__ = sd.bool_for_default('OGoAccessManagerDebugEnabled')
        self._ctx = ctx
        self.init_cache()

    def init_cache(self):
        self._cache = { }

    def clear_cache(self):
        self._cache = { }

    def set_cached_access(self, entity, rights):
        if (hasattr(entity, 'object_id')):
            self._cache[entity.object_id] = rights

    def get_cached_access(self, entity):
        if (hasattr(entity, 'object_id')):
            self._cache.get(entity.object_id, None)
        return None

    @property
    def debug(self):
        return AccessManager.__DebugOn__

    def filter_by_access(self, rights, entities, **params):

        result = [ ]

        if ( not ( isinstance(entities, list) ) ):
            entities = [ entities ]

        start = time.time()

        # The "one_kind_hack" param lets us avoid calling the TypeManager,
        # which saves time [potentially a lot of time].  The caller can
        # specify this when it knows for certain all the objects in the
        # collection are of the specified type. The value of the one_kind_hack
        # parameter must be a valid case-sensitive entity name, like "Contact"

        if params.has_key('one_kind_hack'):
            objects = { params['one_kind_hack']: entities }
        else:
            objects = self._ctx.type_manager.group_by_type(objects=entities)

        # Establish the security context(s) for the evaluation
        if params.get('contexts', None):
            if self._ctx.is_admin:
                # An admin user may specify any set of constraining contexts they like
                context_ids = set( [ int(x) for x in params.get('contexts') ] )
            else:
                # You can only specify contexts the user posesses (is a member of), other contexts get
                # silently dropped.
                context_ids = set( [ int(x) for x in params.get('contexts') ] ).intersection(set(self._ctx.context_ids) )
        else:
            # Default to all the contexts the user posesses
            context_ids = self._ctx.context_ids

        for kind in objects.keys():
            manager = BundleManager.get_access_manager(kind, self._ctx)
            if (self.debug):
                self.log.debug('filtering {0} using {1}'.format(kind, repr(manager)))
            x = manager.materialize_rights(objects=objects[kind], contexts=context_ids)
            start_filter = time.time()
            for k in x.keys():
                if (set(list(rights.lower())).issubset(x[k])):
                    result.append(k)
            duration = (time.time() - start_filter)

            if (self._ctx.amq_available):
                self._ctx.send(None, 'coils.administrator/performance_log', { 'lname':   'access',
                                                                              'oname':   kind,
                                                                              'runtime': duration,
                                                                              'error':   False } )
        if (self.debug):
            self.log.debug('access filter returning %d of %d objects' % (len(result), len(entities)))
            end = time.time()
            self.log.debug('%s: duration of filter_by_access was %0.3fs' % (repr(self), (end - start)))
        return result

    def access_rights(self, entity, **params):

        # Establish the security context(s) for the evaluation
        if params.get('contexts', None):
            if self._ctx.is_admin:
                # An admin user may specify any set of constraining contexts they like
                context_ids = set( [ int(x) for x in params.get('contexts') ] )
            else:
                # You can only specify contexts the user posesses (is a member of), other contexts get
                # silently dropped.
                context_ids = set( [ int(x) for x in params.get('contexts') ] ).intersection(set(self._ctx.context_ids) )
        else:
            # Default to all the contexts the user posesses
            context_ids = self._ctx.context_ids

        result = { }
        rights = self.get_cached_access(entity)
        if (rights is None):
            manager = BundleManager.get_access_manager(entity.__entityName__, self._ctx)
            rights = manager.materialize_rights(objects=[entity], contexts=context_ids)
            self.set_cached_access(entity, rights[entity])
            return rights[entity]
        else:
            if (self.debug):
                self.log.debug('Got access rights from cache')
            return rights
