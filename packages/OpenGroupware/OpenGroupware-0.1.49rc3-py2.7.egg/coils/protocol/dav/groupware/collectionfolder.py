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
import hashlib
from coils.core                        import Contact, \
                                              Enterprise, \
                                              Document, \
                                              Folder, \
                                              Note, \
                                              Project, \
                                              Task
from coils.net                         import DAVFolder, \
                                              DAVObject, \
                                              DAVFolder
from projectfolder                     import ProjectFolder
from documentsfolder                   import DocumentsFolder
from documentobject                    import DocumentObject
from contactobject                     import ContactObject
from eventobject                       import EventObject


BANNED_OBJECT_IDS = [ 10000, 8999 ]

TYPE_FACTORY =  { 'Project':     ProjectFolder,
                  'Folder':      DocumentsFolder,
                  'Contact':     ContactObject,
                  'Appointment': EventObject,
                  'Document':    DocumentObject }

class CollectionFolder(DAVFolder):
    ''' Provides a WebDAV collection containing all the projects (as
        subfolders) which the current account has access to,'''

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        ''' Enumerates projects using account::get-projects.'''
        #print 'Self: {0}'.format(self.entity)
        contents =  self.context.run_command('collection::get-assignments', collection=self.entity,
                                                                            as_entity=True)
        #print 'Found {0} children'.format(len(contents))
        if (contents is not None):
            for entity in contents:
                if entity.__entityName__ in TYPE_FACTORY and entity.object_id not in BANNED_OBJECT_IDS:
                    display_name = entity.get_display_name()
                    if display_name is not None:
                        self.insert_child(entity.object_id, entity, alias=display_name)
            #print 'Load complete'
            return True
        else:
            #print 'contents is None'
            return False

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self._get_ctag()

    def _get_ctag(self):
        return '{0}:{1}'.format(self.entity.object_id, self.entity.version)

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == '.ctag'):
            # TODO: 
            return StaticObject(self, '.ctag', context=self.context,
                                                request=self.request,
                                                payload=self._get_ctag(),
                                                mimetype='text/plain')
        if (auto_load_enabled):
            if (self.load_contents()):
                if (self.has_child(name)):
                   # WebDAV collection
                    tmp = self.get_child(name)
                    if tmp:
                        if tmp.__entityName__ in TYPE_FACTORY:
                            return TYPE_FACTORY[tmp.__entityName__](self, name, entity=tmp,
                                                                                parameters=self.parameters,
                                                                                request=self.request,
                                                                                context=self.context)
                else:
                    pass
                    #print 'no child found for name "{0}"'.format(name)
        self.no_such_path()
