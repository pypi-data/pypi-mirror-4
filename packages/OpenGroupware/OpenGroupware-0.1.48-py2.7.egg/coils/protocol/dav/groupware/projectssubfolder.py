#
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
import hashlib
from coils.net                         import DAVFolder
from coils.core                        import Project, CoilsException
from groupwarefolder                   import GroupwareFolder
import projectfolder

class ProjectsSubFolder(DAVFolder, GroupwareFolder):
    ''' Provides a WebDAV collection containing all the projects (as
        subfolders) which the current account has access to,'''

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def __repr__(self):
        return '<ProjectsSubFolder projectId="{0}" projectName="{1} projectNumber="{2}"/>'.\
            format(self.entity.object_id, self.entity.name, self.entity.number)

    def _load_contents(self):
        children = self.context.run_command('project::get-projects', project=self.entity)
        for project in children:
            self.insert_child(project.number, project, alias=project.object_id)
        return True

    def _get_project_for_key(self, key):
        try:
            object_id = int(str(key).split('.')[0])
        except:
            # TODO: Raise an exception
            pass
        project = self.context.run_command('project::get', id = object_id)

    def _get_project_for_name(self, name):
        project = self.context.run_command('project::get', number=name)
        if not project:
            project = self.context.run_command('project::get', name=name)
            if not project:
                try:
                    project = self.context.run_command('project::get', id=int(name))
                except:
					project = None
        if project:
            if project.parent_id == self.entity.object_id:
                return project
        return None

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self._get_ctag()

    def _get_ctag(self):
        if (self.load_contents()):
            m = hashlib.md5()
            for entry in self.get_children():
                m.update('{0}:{1}'.format(entry.object_id, entry.version))
            return unicode(m.hexdigest())
        return u'0'

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (self.is_loaded):
            project = self.get_child(name)
        else:
            project = self._get_project_for_name(name)
            if (project is None):
                name = name.replace('(', '%28').replace(')', '%29')
                project = self._get_project_for_name(name)
        if (project is None):
            self.no_such_path()
        else:
            return projectfolder.ProjectFolder(self, project.number,
                                 entity=project,
                                 parameters=self.parameters,
                                 request=self.request,
                                 context=self.context)

    #
    # MKCOL
    #

    def do_MKCOL(self, name):
        ''' Create a collection with the specified name. '''
        
        project = self.context.run_command('project::get', number=name)
        
        # If we already found a project with this numer then what we really
        # want is to re-parent that project to the current project context
        # Otherwise we are creating a new child project
        if project:
			# TODO: Verify write access to the project
			project = self.context.run_command('project::set', object=project,
                                                               values={ 'parent_id': self.entity.object_id } )
        else:
            project = self.context.run_command('project::new', values = { 'name': name, 
                                                                          'number': name,
                                                                          'parent_id': self.entity.object_id } )
            self.context.run_command('project::set-contacts', project=project, 
                                                              contact_ids = [ self.context.account_id ] )
        self.context.commit()
        self.request.simple_response(201)

    #
    # MOVE
    #

    def do_MOVE(self, name):
        # See Issue#158
        # TODO: Support the Overwrite header T/F

        source, target, target_name, overwrite = self.move_helper(name)

        self.log.debug('Request to move "{0}" to "{1}" as "{2}".'.format(source, target, target_name))

        ''' The item being moved (the source):
            1. Must be a project.
            2. Cannot be the same project it is being moved to
            3. Must be being moved here (should always be true, but we check anyway)
            4. The project being moved is not a parent of us [TODO]
            5. 
        '''
    

        if (isinstance(source.entity, Project) and 
            source.entity != self.entity):
				
            # We are moving a project from another location to be a
            # child of this folder's Project (self.entity)
            # This is the only type of move supported in this context

            if overwrite:
				# TODO: Does this mean anything in this case? Probably not.
                #       If a project of the same number exists we are just
                #       going to error anyway.
				pass
				
			# TODO: Implement check #4
				
            # If the name of the project being moved is "Untitled Folder" then we update the
            # name of the Project as well as the number.  This is because Naulitus/GVFS on a 
            # make-new-folder operation always first creates a folder named "Untitle Folder" an
            # then renames is - so to avoid multiple Projects named "Untitled Folder" we implement
            # this hack.
            
            values = { 'number': target_name,
                       'parent_id': self.entity.object_id }
            if source.entity.name == 'Untitled Folder':
                values['name'] = target_name                
                
            result = self.context.run_command('project::set', object=source.entity,
                                                              values=values )
            self.context.commit()
            self.request.simple_response(204)
            return
                
        raise CoilsException('Moving {0} via WebDAV is not supported in this context'.format(source.entity))
