#
# Copyright (c) 2009, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from get_project      import GetProject
from accessmanager    import ProjectAccessManager
from get_root_folder  import GetProjectRootFolder
from get_notes        import GetProjectNotes
from get_tasks        import GetProjectTasks
from search_project   import SearchProjects
from get_actions      import GetProjectTaskActions      # project::get-task-actions
from get_contacts     import GetProjectContacts         # project::get-contacts
from set_contacts     import SetProjectContacts         # project::set-contacts
from get_enterprises  import GetProjectEnterprises      # project::get-enterprises
from set_enterprises  import SetProjectEnterprises      # project::set-enterprises
from create_project   import CreateProject              # project::new
from update_project   import UpdateProject              # project::set
from get_path         import GetProjectPath             # project::get-path
from get_projects     import GetChildProjects           # project::get-projects
from get_favorites    import GetFavorites               # project::get-favorite
from set_favorite     import SetFavorite                # project::set-favorite
from delete_project   import DeleteProject              # project::delete
from assign_company   import AssignEnterpriseToProject  # project::assign-enterprise
from assign_company   import AssignContactToProject     # project::assign-contact
from unassign_company import UnassignEnterpriseFromProject  # project::unassign-enterprise
from unassign_company import UnassignContactFromProject     # project::unassign-contact
