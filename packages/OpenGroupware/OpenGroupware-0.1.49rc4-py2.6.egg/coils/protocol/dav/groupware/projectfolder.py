#
# Copyright (c) 2009, 2010, 2011, 2012 
# Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.net                         import DAVFolder, EmptyFolder
from contactsfolder                    import ContactsFolder
from tasksfolder                       import TasksFolder
from documentsfolder                   import DocumentsFolder
from notesfolder                       import NotesFolder
from rss_feed                          import ProjectTaskActionsRSSFeed
import  projectssubfolder

class ProjectFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def __repr__(self):
		return '<ProjectFolder contextId="{0}" login="{1}" projectId="{2}" projectName="{3}" contextId="{4}" login="{5}"/>'.\
                format( self.context.account_id, 
                        self.context.login, 
                        self.entity.object_id, 
                        self.entity.name,
                        self.context.account_id,
                        self.context.login)

    def _load_contents(self):
        ua = self.context.user_agent_description
        if ua['webdav']['showProjectTasksFolder']:
            self.insert_child('Tasks', None, alias='Tasks')
        if ua['webdav']['showProjectNotesFolder']:
            self.insert_child('Notes', None)
        if ua['webdav']['showProjectContactsFolder']:
            self.insert_child('Contacts', None)
        if ua['webdav']['showProjectDocumentsFolder']:
            self.insert_child('Documents', None)
        if ua['webdav']['showProjectEnterprisesFolder']:
            self.insert_child('Enterprises', None)
        if ua['webdav']['showProjectVersionsFolder']:
            self.insert_child('Versions', None)
        if ua['webdav']['showProjectProjectsFolder']:
            self.insert_child('Projects', None)
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == 'actions.rss'):
            return ProjectTaskActionsRSSFeed(self, name, self.entity,
                                              request=self.request,
                                              context=self.context)
        elif (name == 'Documents'):
            folder = self.context.run_command('project::get-root-folder', project=self.entity)
            if (folder is None):
                self.no_such_path()
            return DocumentsFolder(self, name,
                                    entity=folder,
                                    parameters=self.parameters,
                                    request=self.request,
                                    context=self.context)
        elif (name == 'Notes'):
            return NotesFolder(self, name,
                                entity=self.entity,
                                parameters=self.parameters,
                                request=self.request,
                                context=self.context)
        elif (name == 'Tasks'):
            return TasksFolder(self, name,
                                entity=self.entity,
                                parameters=self.parameters,
                                request=self.request,
                                context=self.context)
        elif (name == 'Contacts'):
            return ContactsFolder(self, name,
                                   entity=self.entity,
                                   parameters=self.parameters,
                                   request=self.request,
                                   context=self.context)
        elif (name == 'Projects'):
            return projectssubfolder.ProjectsSubFolder(self, name,
                                     entity=self.entity,
                                     parameters=self.parameters,
                                     request=self.request,
                                     context=self.context)
        else:
            return EmptyFolder(self, name,
                                entity=self.entity,
                                parameters=self.parameters,
                                request=self.request,
                                context=self.context)
