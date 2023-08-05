#
# Copyright (c) 2009, 2010, 2011, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime import datetime
import pytz, time
from coils.foundation  import *
from coils.core        import *
from coils.net         import *
#from render import Render
#from render_object import as_string, as_datetime, as_integer
#from render_account import render_account
#from render_timezone import render_timezone
from coils.core.omphalos import *

ZOGI_DEFAULT_SEARCH_LIMIT = 150

class API(Protocol):
    __pattern__   = 'RPC2'
    __namespace__ = 'zogi'
    __xmlrpc__    = True

    def __init__(self, context):
        self.context = context
        self.context.log.debug('zOGI API Handler Marshalled')
        self.api = ZOGIAPI(self.context)

    #
    # Public API
    #

    def getAuditEntries(self, floor):
        # TODO: Implement
        return [ ]

    def getFavoritesByType(self, kind, detail):
        kind = kind.lower()
        if (kind in ['contact', 'enterprise', 'project']):
            x = self.context.run_command('{0}::get-favorite'.format(kind))
            if (len(x) > 0):
                result = Render.Results(x, detail, self.context)
                return result
        return [ ]

    def unflagFavorites(self, ids):
        # TODO: Implement
        # ids may be an array of IDs or a CSV string of IDs
        # What is the return value of this very rarely used function?
        return None

    def flagFavorites(self, ids):
        # TODO: Implement
        # ids may be an array of IDs or a CSV string of IDs
        # What is the return value of this very rarely used function?
        return None

    def getLoginAccount(self, detail=65535):
        # Status: Implemeted
        # http://code.google.com/p/zogi/wiki/getLoginAccount
        account  = self.context.run_command('account::get')
        defaults = self.context.run_command('account::get-defaults')
        return render_account(account, defaults, detail, self.context)

    def getObjectById(self, object_id, detail_level, flags = {}):
        print 'getObjectById', object_id, detail_level
        # Status: Implemented
        # 'objectId=%d level=%d' % (object_id, detail_level)
        if not detail_level:
            detail_level = 0
        kind = self.context.type_manager.get_type(object_id)
        if (kind == 'Unknown'):
            result = { 'entityName': 'Unknown', 'objectId': object_id }
        else:
            x = getattr(self.api, 'get_%ss_by_ids' % kind.lower())([object_id])
            if ((x is not None) and (len(x) == 1)):
                result = Render.Result(x[0], detail_level, self.context)
            else:
                result = { 'entityName': 'Unknown', 'objectId': object_id }
        return result

    def getObjectsById(self, object_ids, detail_level, flags={}):
        # Status: Implemented
        result = [ ]
        index = self.context.type_manager.group_ids_by_type(object_ids)
        for key in index.keys():
            x = getattr(self.api, 'get_%ss_by_ids' % key.lower())(index[key])
            if (x is None):
                self.context.log.debug('result of Logic was None')
            else:
                self.context.log.debug('retrieved %d %s objects' % (len(x), key))
                result.extend(x)
        result = Render.Results(result, detail_level, self.context)
        return result

    def getNotifications(self, start, end):
        # TODO: Implement
        # http://code.google.com/p/zogi/wiki/getNotifications
        return [ ]

    def getObjectVersionsById(self, ids):
        return self.api.get_object_versions_by_id(ids)

    def listObjectsByType(self, kind, list_name):
        return self.api.list_objects_by_type(kind, list_name)

    def getTombstone(self, object_id):
        return self.api.get_tombstone(object_id, { })

    def getTypeOfObject(self, object_id):
        # TODO: Implement
        # http://code.google.com/p/zogi/wiki/getTypeOfObject
        object_id = int(object_id)
        return self.context.type_manager.get_type(object_id)

    def putObject(self, payload):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/putObject
        if (isinstance(payload, dict)):

            if (payload.has_key('entityName')):
                entity_name = payload['entityName'].lower()

            if payload.has_key('_FLAGS'):
                flags = payload['_FLAGS']
                if isinstance(flags, basestring):
                    flags = flags.split(',')
            else:
                flags = []

            if self.context.user_agent_description['omphalos']['associativeLists']:
                payload = disassociate_omphalos_representation(payload)

            result = getattr(self.api, 'put_%s' % entity_name)(payload, flags)

            if result:
                self.context.commit()
            result = Render.Result(result, 65535, self.context)
        else:
            raise CoilsException('Put entity has not entityName attribute')
        return result

    def deleteObject(self, payload, flags={}):
        # TODO: Implement
        # payload can be an object Id or an actual object
        # http://code.google.com/p/zogi/wiki/deleteObject
        if (isinstance(payload, int) or isinstance(payload, basestring)):
            object_id = int(payload)
        else:
            object_id = int(payload.get('objectId'))
        kind = self.context.type_manager.get_type(object_id)
        x = getattr(self.api, 'delete_%s' % kind.lower())(object_id, flags)
        if (x is None):
            return False
        self.context.commit()
        return x

    def searchForObjects(self, kind, criteria, detail, flags=None):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/searchForObjects
        # Set-up default flags
        full_flags = { 'limit': 100, 'revolve': False, 'filter': None }
        # If flags were provided by the call read those overtop our default flags
        if isinstance(flags, dict):
            full_flags['limit'] = flags.get('limit', 100)
            full_flags['filter'] = flags.get('filter', None)
            if flags.get('revolve', 'NO') == 'YES':
                full_flags['revolve'] = True
        # Do Search
        start = time.time()
        x = getattr(self.api, 'search_%s' % kind.lower())(criteria, full_flags)
        self.context.log.info('searchForObjects search command consumed {0}s'.format(time.time() - start))
        # Process results of search
        result = [ ]
        start = time.time()
        if (len(x) > 0):
            for y in x:
                if (hasattr(y, '__entityName__')):
                    # Result contains ORM
                    z = Render.Result(y, detail, self.context)
                    if (z is not None):
                        result.append(z)
                else:
                    result.append(y)
        self.context.log.info('Rendering searchForObjects results consumed {0}s'.format(time.time() - start))
        self.context.log.info('searchForObjects returning {0} entities'.format(len(result)))
        result = self.api.process_eo_filter(result, full_flags['filter'])
        return result

