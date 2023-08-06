#
# Copyright (c) 2010, 2011, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core                        import Process
from coils.net                         import DAVFolder, \
                                              OmphalosCollection
from routesfolder                      import RoutesFolder
from formatsfolder                     import FormatsFolder
from mapsfolder                        import MapsFolder
from tablesfolder                      import TablesFolder
from loadschedule                      import LoadScheduleObject
from schedulefolder                    import ScheduleFolder
from xsdfolder                         import XSDFolder
from xsltfolder                        import XSLTFolder
from wsdlfolder                        import WSDLFolder

WORKFLOW_SUBFOLDERS = { 'Routes':   RoutesFolder,   'Formats': FormatsFolder,
                        'Schedule': ScheduleFolder, 'Maps':    MapsFolder,
                        'XSD':      XSDFolder,      'Tables':  TablesFolder,
                        'WSDL':     WSDLFolder,     'XSLT':    XSLTFolder,     }

class WorkflowFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        for key, value in WORKFLOW_SUBFOLDERS.items( ):
            self.insert_child( key, value )
        return True

    def return_process_list(self, name):
        route_group = self.parameters.get( 'routegroup', None )
        if route_group:
            route_group = route_group[ 0 ]
        if 'all' in self.parameters:
            # TODO: Add support for filtering by routegroup (maybe in the Logic level / access manager)
            if route_group:
                ps = self.context.run_command( 'process::list', properties=[ Process ] )
            else:
                ps = self.context.run_command( 'process::list', properties=[ Process ], route_group=route_group )
        else:
            # NOTE: process:get does not support specification of a route group parameter
            ps = self.context.run_command( 'process::get', route_group = route_group )
        if ( 'detail' in self.parameters ) and ( len( self.parameters[ 'detail' ] ) ):
            detail_level = int( self.parameters[ 'detail' ][ 0 ] )
        else:
            detail_level = 65535 - 2048
        return OmphalosCollection( self, name,
                                   detailLevel=detail_level,
                                   rendered=True,
                                   data=ps,
                                   parameters=self.parameters,
                                   context=self.context,
                                   request=self.request )

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name in WORKFLOW_SUBFOLDERS:
            return WORKFLOW_SUBFOLDERS[ name ]( self, name,
                                                parameters=self.parameters,
                                                request=self.request,
                                                context=self.context )
        elif (name == '.ps'):
            return self.return_process_list( name )
        return self.no_such_path()
