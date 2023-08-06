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
from datetime                          import datetime
from coils.foundation                  import CTag
# DAV Classses
from coils.net                         import DAVFolder
from teamobject                        import TeamObject
from groupwarefolder                   import GroupwareFolder

class TeamsFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__( self, parent, name, **params )

    @property
    def managed_entity(self):
        return 'Team'

    # PROP: GETCTAG

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag( )

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag( )

    def get_property_caldav_getctag(self):
        return self.render_key_ctag( )

    def _load_contents(self):
        teams = self.context.run_command( 'team::get' )
        for team in teams:
            self.insert_child( team.object_id, team, alias='{0}.vcf'.format( team.object_id ) )
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name.startswith( '.' ):
            function_name = 'render_key_{0}'.format( name[ 1: ].lower().replace( '.', '_' ) )
            if hasattr( self, function_name ):
                return getattr( self, function_name )( name, is_webdav=is_webdav, auto_load_enabled=auto_load_enabled ) 
            else:
                self.no_such_path( )
        elif self.load_contents( ):
            team = self.get_child(name)
            if (team is not None):
                return self.get_entity_representation( name, team, is_webdav=is_webdav )
        self.no_such_path()
