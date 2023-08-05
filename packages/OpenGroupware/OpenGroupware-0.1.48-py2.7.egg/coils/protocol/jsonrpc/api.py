#!/usr/bin/env python
# Copyright (c) 2011, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import time
from coils.foundation    import *
from coils.core          import *
from coils.net           import *
from coils.core.omphalos import Render         as Omphalos_Render
from coils.core.omphalos import render_account as Omphalos_RenderAccount

def Caseless_Get(dict_, key_):
    if key_ in dict_:
        value= dict_[key_]
    else:
        for key, value in dict_.items():
            if key_.lower() == key.lower():
                value = dict_[key]
                break
        else:
            value = None
    return value

class API(object):

    def __init__(self, context):
        self.context = context
        self.api     = ZOGIAPI(self.context)

    def _apply_defaults(self, parameters, defaults):
        result = [ ]
        for i in range(0, len(defaults)):
            if (len(parameters) > i):
                result.append(parameters[i])
            else:
                result.append(defaults[i])
        return result

    def api_gettombstone(self, args):
        # TODO: Check there is a single argument
        return self.api.get_tombstone(args[0], { })

    def api_getfavoritesbytype(self, parameters):
        parameters = self._apply_defaults(parameters, ('Contact', 0))
        parameters[0] = parameters[0].lower()
        if (parameters[0] in ['contact', 'enterprise', 'project']):
            x = self.context.run_command('{0}::get-favorite'.format(parameters[0]))
            if (len(x) > 0):
                result = Omphalos_Render.Results(x, parameters[1], self.context)
                return result
        return [ ]

    def api_getloginaccount(self, params):
        # Status: Implemeted
        account = self.context.run_command('account::get')
        defaults = self.context.run_command('account::get-defaults')
        return Omphalos_RenderAccount(account, defaults, 65503, self.context)

    def api_getobjectbyid(self, parameters):
        # Parameters: object id, detail level, flags
        # Status: Implemented
        parameters = self._apply_defaults( parameters, ( self.context.account_id, 0, { } ) )
        kind = self.context.type_manager.get_type( parameters[ 0 ] )
        if kind == 'Unknown':
            result = { 'entityName': 'Unknown', 'objectId': parameters[0] }
        else:
            method = getattr( self.api, 'get_{0}s_by_ids'.format( kind.lower( ) ) )
            result = method( [ parameters[ 0 ]  ] )
            if result:
                result = Omphalos_Render.Result( result[ 0 ], parameters[ 1 ], self.context )
            else:
                result = { 'entityName': 'Unknown', 'objectId': parameters[ 0 ] }
        return result

    def api_getobjectsbyid(self, parameters):
        # Status: Implemented
        parameters = self._apply_defaults( parameters, ( [ self.context.account_id ], 0 ) )
        result = [ ]
        index = self.context.type_manager.group_ids_by_type( parameters[ 0 ] )
        for key in index.keys( ):
            method = getattr( self.api, 'get_{0}s_by_ids'.format( key.lower( ) ) ) 
            tmp = method( index[ key ] )
            if not tmp:
                self.context.log.debug( 'result of Logic was None' )
            else:
                self.context.log.debug( 'retrieved {0} {1} objects'.format( len( x ), key ) )
                result.extend( tmp )
        result = Omphalos_Render.Results( result, parameters[ 1 ], self.context )
        return result

    def api_putobject(self, parameters):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/putObject
        parameters = self._apply_defaults(parameters, (None, {}))
        payload = parameters[0]
        if (isinstance(payload, dict)):
            for key in ['entityName', 'entityname', 'ENTITYNAME']:
                if payload.has_key(key):
                    entity_name = payload[key].lower()
                    break

            for key in ['_FLAGS', '_flags', '_Flags']:
                if (payload.has_key(key)):
                    flags = payload[key]
                    if (isinstance(flags, basestring)):
                        flags = flags.split(',')
                    break
            else:
                flags = []
            result = getattr( self.api, 'put_{0}'.format( entity_name ) )( payload, parameters[1] )
            if (result is not None):
                self.context.commit()
            result = Omphalos_Render.Result(result, 65535, self.context)
        else:
            raise CoilsException('Put entity has not entityName attribute')
        return result

    def api_deleteobject(self, parameters):
        # payload can be an object Id or an actual object
        # http://code.google.com/p/zogi/wiki/deleteObject
        if not parameters:
            raise CoilsException('no parameters provided to deleteObject')
        kind = object_id = None
        payload = parameters[0]
        flags   = parameters[1] if len(parameters) == 2 else { }
        if (isinstance(payload, int) or isinstance(payload, basestring)):
            payload = int(payload)
            kind = self.context.type_manager.get_type(payload)
        elif isinstance(payload, dict):
            object_id = Caseless_Get(payload, 'objectId')
            if object_id:
                # Do not trust the client, if the dict has an object-id then we look-up the type
                kind = self.context.type_manager.get_type(object_id)
                payload = object_id
            else:
                # get the type from the dict, this may be an improper entity such as an objectProperty
                kind = Caseless_Get(payload, 'entityName')
        else:
           raise CoilsException('Unable to comprehend parameters provided to deleteObject')
        if kind:
            x = getattr(self.api, 'delete_{0}'.format(kind.lower()))(payload, flags)
            if (x is None):
                return False
            self.context.commit()
            return True
        else:
            raise CoilsException('Unable to determine id and/or type for call to deleteObject')

    def api_searchforobjects(self, parameters):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/searchForObjects
        parameters = self._apply_defaults(parameters, ('Contact', [], 0, {}))
        flags = parameters[3]
        full_flags = { 'limit': 100, 'revolve': False, 'filter': None }
        # If flags were provided by the call read those overtop our default flags
        if isinstance(flags, dict):
            full_flags['limit'] = flags.get('limit', 100)
            full_flags['filter'] = flags.get('filter', None)
            if flags.get('revolve', 'NO') == 'YES':
                full_flags['revolve'] = True
        else:
            # Flags is not a dictionary!
            pass
        x = getattr(self.api, 'search_%s' % parameters[0].lower())(parameters[1], full_flags)
        result = [ ]
        start = time.time()
        if (len(x) > 0):
            for y in x:
                if (hasattr(y, '__entityName__')):
                    # Result contains ORM
                    z = Omphalos_Render.Result(y, parameters[2], self.context)
                    if (z is not None):
                        result.append(z)
                else:
                    result.append(y)
        self.context.log.info('Rendering searchForObjects results consumed {0}s'.format(time.time() - start))
        self.context.log.info('searchForObjects returning {0} entities'.format(len(result)))
        result = self.api.process_eo_filter(result, full_flags['filter'])
        return result


    def getNotifications(self, start, end):
        # TODO: Implement
        # http://code.google.com/p/zogi/wiki/getNotifications
        return [ ]

    def api_gettypeofobject(self, parameters):
        # http://code.google.com/p/zogi/wiki/getTypeOfObject
        object_id = int (parameters[0])
        return self.context.type_manager.get_type(object_id)

    def api_unflagfavorites(self, parameters):
        if parameters:
            object_ids = parameters[0]
        else:
            raise CoilsException('No parameters specified for unflagFavorites')
        if isinstance(object_ids, basestring):
            object_ids = object_ids.split(',')
        if not isinstance(object_ids, list):
            raise CoilsException('Unable to parse objectId parameter.')
        object_ids = [ int(x) for x in object_ids ]
        for object_id in object_ids:
            self.context.unfavorite(object_id)
        return True

    def api_flagfavorites(self, parameters):
        if parameters:
            object_ids = parameters[0]
        else:
            raise CoilsException('No parameters specified for flagFavorites')
        if isinstance(object_ids, basestring):
            object_ids = object_ids.split(',')
        if not isinstance(object_ids, list):
            raise CoilsException('Unable to parse objectId parameter.')
        object_ids = [ int(x) for x in object_ids ]
        for object_id in object_ids:
            self.context.favorite(object_id)
        return True

    def api_listobjectsbytype(self, parameters):
        if len(parameters):
            kind = str(parameters[0])
            if len(parameters) > 1:
                list_name = str(parameters[1])
            else:
                list_name = None
            return self.api.list_objects_by_type(kind, list_name)
        raise CoilsException('Invalid method signature, first parameter just be an entity name.')
        
    def api_getperformance(self, parameters):
        return self.api.get_performance( parameters[ 0 ] )
        
    def api_ps(self, parameters):
        return self.api.ps( )
