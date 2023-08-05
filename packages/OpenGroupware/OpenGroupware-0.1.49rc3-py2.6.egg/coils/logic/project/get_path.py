#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetProjectPath(GetCommand):
    __domain__ = "project"
    __operation__ = "get-path"

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        self._project = params.get('project', None)
        self._path    = params.get('path', None)
        self._create  = params.get('create', False)
        if (self._project is None) or (self._path is None):
            raise CoilsException('No project or path provided to project::get-path')

    def run(self, **params):
        self.set_single_result_mode()
        if (isinstance(self._path, basestring)):
            components = self._path.split('/')[1:]
        elif (isinstance(self._path, list)):
            components = self._path
        else:
            raise CoilsException('Path of unexpected type "{0}".'.format(self._path))
        entity = self._ctx.run_command('project::get-root-folder', project=self._project)
        if not entity:
            raise CoilsException('Unable to resolve root folder for projectId#{0}'.format(self._project.object_id))
        for component in components:
            if (entity.__entityName__ == 'Folder'):
                result = self._ctx.run_command('folder::ls', id=entity.object_id, name=component)
                if ((len(result) == 0) and (self._create)):
                    # TODO: Check that the current context has permissions to create a subfolder
                    self.log.debug('Creating new folder for path; component is "{0}".'.format(component))
                    entity = self._ctx.run_command('folder::new', folder = entity,
                                                                  values = { 'name': component } )
                    if not entity.object_id: raise CoilsException('Folder object created with no objectId')
                    if not entity.folder_id: raise CoilsException('Folder object created with no folderId')
                    if (entity is None):
                        self.log.debug('Failed to create path component "{0}" for path "{1}".'.format(component, self._path))
                elif (len(result) == 1):
                    entity=result[0]
                    self.log.debug('Found {0} for path component "{1}".'.format(entity, component))
                else:
                    entity = None
                    break
            else:
                entity = None
                break
        self.log.debug('Returning {0} for path "{1}"'.format(entity, self._path))
        self.set_return_value(entity)
