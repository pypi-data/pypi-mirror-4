#
# Copyright (c) 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime               import datetime
from pkg_resources          import Requirement, resource_filename
from coils.foundation       import ServerDefaultsManager, Project, OGO_ROLE_SYSTEM_ADMIN
from exception              import CoilsException, NotImplementedException, CoilsBusException


'''

  Workflow Developers     : wfdev : OGoWorkflowDevelopersTeam
  Workflow Adminsitrators : wflad : OGoWorkflowAdministrativeTeam
  Help Desk               : helpd : OGoHelpDeskRoleName
  System Administrators   : admin : OGoAdministrativeTeam
  All Users               : users :
'''

EXCHANGE_NAME = 'OpenGroupware_Coils'
EXCHANGE_TYPE = 'direct'

FOLDER_TREE = [ { 'name': 'Entity Templates',
                  'permissions': [ ( 'admin', 'rwdaip', ),
                                   ( 'users', 'rlv',    ), ],
                  'children': [ { 'name': 'Task',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'users', 'rlv',  ), ],
                                },
                                { 'name': 'Contact',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'users', 'rlv',  ), ],
                                },
                                { 'name': 'Enterprise',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'users', 'rlv',  ), ],
                                },
                                { 'name': 'Project',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'users', 'rlv',  ), ],
                                },
                                { 'name': 'Collection',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'users', 'rlv',  ), ],
                                }, ],
                },
                { 'name': 'Wiki',
                  'permissions': [ ( 'admin', 'rwdaip', ),
                                   ( 'netwk', 'rlv',    ) ],
                  'children': [ ],
                  'content': [ { 'name': 'default.css',
                                 'source': 'coils/resources/wiki/default.css',
                                 'permissions': [ ( 'netwk', 'rlv',    ),
                                                  ( 'admin', 'rwadlv', ), ],
                               },
                               { 'name': 'index.markdown',
                                 'source': 'coils/resources/wiki/index.markdown',
                                 'permissions': [ ( 'netwk', 'rlv',    ),
                                                  ( 'admin', 'rwadlv', ), ],
                               },
                               { 'name': 'sortable.js',
                                 'source': 'coils/resources/wiki/sorttable.js',
                                 'permissions': [ ( 'netwk', 'rlv',    ),
                                                  ( 'admin', 'rwadlv', ), ],
                               }, ]
                },
                { 'name': 'Sites',
                  'permissions': [ ( 'admin', 'rwdaip', ),
                                   ( 'netwk', 'lv', ), ],
                  'content': [ { 'name': 'RedirectorMap.yaml',
                                 'source': 'coils/resources/redirectormap.yaml',
                                 'permissions': [ ( 'netwk', 'rlv',    ),
                                                  ( 'admin', 'rwadlv', ),
                                                  ( 'wflad', 'rwlv',   ), ], },
                             ],
                },
                { 'name': 'Workflow',
                  'permissions': [ ( 'wflad', 'rwdaip', ),
                                   ( 'wfdev', 'rlv', ),
                                   ( 'sysad', 'rwdaip', ), ],
                  'children': [ { 'name': 'Reports',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'sysad', 'rwda', ), ],
                                   'content': [ { 'name': 'tasks.startofday.mako',
                                                  'source': 'coils/resources/reports/task.startofday.mako',
                                                  'permissions': [ ],
                                                },
                                                { 'name': 'tasks.endofday.mako',
                                                  'source': 'coils/resources/reports/task.endofday.mako',
                                                  'permissions': [ ],
                                                },
                                              ],
                                },
                                { 'name': 'Templates',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'sysad', 'rwda', ),
                                                   ( 'users', 'rlv',  ), ],
                                },
                                { 'name': 'Transforms',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'sysad', 'rwda', ),
                                                   ( 'users', 'rlv',  ), ],
                                },
                                { 'name': 'Schemas',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'sysad', 'rwda', ),
                                                   ( 'users', 'rlv',  ), ],
                                },
                                { 'name': 'Tables',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'sysad', 'rwda', ),
                                                   ( 'users', 'rlv',  ), ],
                                },
                                { 'name': 'Formats',
                                  'permissions': [ ( 'wflad', 'rwda', ),
                                                   ( 'wfdev', 'rwd',  ),
                                                   ( 'sysad', 'rwda', ),
                                                   ( 'users', 'rlv',  ), ],
                                }, ],
                }, ]

def get_team_id_for_role( ctx, role, sd=None ):
    if not sd:
        sd = ServerDefaultsManager()
    name = sd.string_for_default( role )
    if name:
        team = ctx.run_command( 'team::get', name=name )
        if team:
            return team.object_id
    return None

class Project7000(object):
    __slots__ = ( 'context', 'roles', 'role_map' )

    def __init__(self, context):
        self.context = context
        sd = ServerDefaultsManager()
        self.load_role_map( )

    def create_project(self):
        project = self.context.run_command( 'project::get', id=7000 )
        if project:
            raise CoilsException( 'Project 7000 (Administrative Root Project) already exists; cannot re-provision.' )
        if not self.context.has_role( OGO_ROLE_SYSTEM_ADMIN ):
            raise CoilsException( 'Administrative role required to provision system projects.' )
        project = Project( )
        project.object_id = 7000
        project.owner_id = 10000
        project.start = datetime.now()
        project.end   = datetime(2032, 12, 31, 18, 59, 59)
        project.kind = 'coils.system'
        project.number = 'P7000@{0}'.format( self.context.cluster_id )
        project.is_fake = 1
        self.context.db_session( ).add( project )
        self.context.run_command('folder::new', values={ 'projectId': 7000, 'name': 'P7000' } )
        #TODO: Complete
        return project

    def refresh_project(self):
        project = self.get_project( )
        if project:
            self.initialize_object_tree( )
            self.context.run_command( 'object::set-acl', object=project, context_id=10003, permissions='rlv' )
            self.context.run_command( 'object::set-acl', object=project, context_id=8999, permissions='lv' )

    def load_role_map(self ):
        self.role_map = { 'users': 10003, 'netwk': 8999 }
        role_workflow_developer, role_workflow_administrator, \
        role_help_desk, role_system_administrator = (
            get_team_id_for_role( self.context, 'OGoWorkflowDevelopersTeam' ),
            get_team_id_for_role( self.context, 'OGoWorkflowAdministrativeTeam' ),
            get_team_id_for_role( self.context, 'OGoHelpDeskRoleName', ),
            get_team_id_for_role( self.context, 'OGoAdministrativeTeam' ) )
        if role_workflow_developer:     self.role_map[ 'wfdev' ] = role_workflow_developer
        if role_workflow_administrator: self.role_map[ 'wflad' ] = role_workflow_administrator
        if role_help_desk:              self.role_map[ 'helpd' ] = role_help_desk
        if role_system_administrator:   self.role_map[ 'admin' ] = role_system_administrator

    def get_project(self):
        project = self.context.run_command( 'project::get', id=7000 )
        if not project:
            if self.context.has_role( OGO_ROLE_SYSTEM_ADMIN ):
                self.create_project( )
            else:
                raise CoilsException( 'Project 7000 (Administrative Root Project) does not exist, please provision' )
        return project

    def _initialize_folder(self, parent, description):
        folder = self.context.run_command( 'folder::ls', folder=parent, name=description[ 'name' ] )
        if folder:
            folder = folder[ 0 ]
        if not folder:
            folder = self.context.run_command( 'folder::new', folder=parent, values={ 'name': description[ 'name' ] } )
        self.reset_object_permissions( folder, description )
        if 'children' in description:
            for child_description in description[ 'children' ]:
                self._initialize_folder( folder, child_description )
        if 'content' in description:
            for content_description in description[ 'content' ]:
                self._initialize_content( folder, content_description )

    def _get_content_stream(self, name):
        pass

    def _initialize_content(self, parent, description):

        def get_content_stream( resource_path ):
            try:
                resource_path = resource_filename( Requirement.parse( "OpenGroupware" ), resource_path )
            except:
                try:
                    handle = open( resource_path, 'rb' )
                except Exception as e:
                    raise e
            else:
                handle = open( resource_path, 'rb' )
            return handle

        document = self.context.run_command( 'folder::ls', folder=parent, name=description[ 'name' ] )
        if document:
            document = document[ 0 ]
            print( 'Content object found, not initializing "{0}"'.format( description[ 'name' ] ) )
        if not document:
            print( 'Creating missing content object "{0}"'.format( description[ 'name' ] ) )
            rfile = get_content_stream( description[ 'source' ] )
            document = self.context.run_command( 'document::new', handle = rfile,
                                                                  folder = parent,
                                                                  values = { },
                                                                  name = description[ 'name' ],
                                                                  annotation = 'provisioned for project7000' )
        self.reset_object_permissions( document, description )

    def reset_object_permissions(self, target, description):
        if 'permissions' in description:
            for role, permissions in description[ 'permissions' ]:
                if role in self.role_map:
                    context_id = self.role_map[ role ]
                    self.context.run_command( 'object::set-acl', object=target,
                                                                 permissions=permissions,
                                                                 context_id=context_id )

    def initialize_object_tree(self):
        project = self.get_project( )
        root_folder = self.context.run_command( 'project::get-root-folder', project=project )
        for description in FOLDER_TREE:
            self._initialize_folder( root_folder, description )
