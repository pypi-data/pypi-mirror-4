#
# Copyright (c) 2011, 2013
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import json, datetime, time
from coils.core           import *
from coils.net            import PathObject, Protocol
from coils.core.omphalos  import Render as Omphalos_Render

def omphalos_encode(o):
    if (isinstance(o, datetime.datetime)):
        return  o.strftime('%Y-%m-%dT%H:%M:%S')
    raise TypeError()


class VistaSearch(Protocol, PathObject):
    __pattern__   = '^vista$'
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def get_name(self):
        return 'vista'

    def is_public(self):
        return False

    def do_HEAD(self):
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=self.entity.get_mimetype(type_map=self._mime_type_map),
                                     headers={ 'etag': 'vista-search' } )

    def do_GET(self):

        include_archived = 'archived' in [ x.lower() for x in self.parameters ]

        if 'type' in self.parameters:
            entity_types = [ 'document' if x.lower()=='file' else x.lower() for x in self.parameters['type'] ]
        else:
            entity_types = None

        search_limit = self.parameters.get('limit', None)
        if search_limit:
            search_limit = int( search_limit[ 0 ] )
        else:
            search_limit = None

        if 'term' in self.parameters:
            keywords = [ x.lower().replace(' ', '\ ') for x in self.parameters['term'] ]
        else:
            keywords = [ self.context.login ]

        project_id = None
        if 'project' in self.parameters:
            value = [ long( x ) for x in self.parameters[ 'project' ] ]
            if value:
                project_id = value[ 0 ]

        detail_level = self.parameters.get('detail', None)
        if detail_level:
            detail_level = int(detail_level[0])
        else:
            # comment + company values
            detail_level = 2056

        start = time.time()
        if project_id:
            # Perform Vista search scoped by a Project
            results = self.context.run_command( 'vista::search', keywords = keywords,
                                                                 entity_types = entity_types,
                                                                 search_limit = 0,
                                                                 project_id = project_id,
                                                                 include_archived = include_archived )
        else:
            #Perform unscoped Vista search
            results = self.context.run_command( 'vista::search', keywords = keywords,
                                                                 entity_types = entity_types,
                                                                 search_limit = 0,
                                                                 include_archived = include_archived )

        end = time.time()
        self.context.send( None,
                           'coils.administrator/performance_log',
                           { 'lname': 'vista',
                             'oname': 'query',
                             'runtime': ( end - start ),
                             'error': False } )

        # We return the number of original results to the client, but we
        # trim the 'rendered' results to less than 100
        result_count = len(results)
        if len(results) > 100:
            results = results[:100]

        start = time.time( )
        results = Omphalos_Render.Results( results, detail_level, self.context )
        results = json.dumps( results, default=omphalos_encode )
        end = time.time( )
        self.context.send( None,
                           'coils.administrator/performance_log',
                           { 'lname': 'vista',
                             'oname': 'render',
                             'runtime': ( end - start ),
                             'error': False } )

        self.request.simple_response( 200,
                                      mimetype='text/plain',
                                      headers={ 'X-OpenGroupware-Coils-Vista-Matches': str( result_count ) },
                                      data=results )

