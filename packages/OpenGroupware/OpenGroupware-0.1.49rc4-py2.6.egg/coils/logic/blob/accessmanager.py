#
# Copyright (c) 2010, 2012
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
from coils.core import EntityAccessManager, ServerDefaultsManager

class BLOBEntityAccessManager(EntityAccessManager):

    __DebugOn__ = None

    def inherited_rights(self, entity, rights):
        if (entity.folder is None):
            return rights
        else:
            permissions = set(list(self.get_acls('allowed', entity.folder)))
            for right in permissions:
                rights.add(str(right))
            denied = self.get_acls('denied', entity)
            rights = rights.difference(denied)
            return self.inherited_rights(entity.folder, rights)

    def project_rights(self, entity, rights):
        if entity.project is None:
            return rights
        elif entity.project.owner_id in self.context_ids:
            # If the context is owner of the project they have full rights to all folders
            rights.add('a') #admin (a)
            rights.add('i') #insert
            rights.add('w') #wrire
            rights.add('m') #modify
            rights.add('d') #delete
            rights.add('r') # ???
            rights.add('f') # ???
        else:
            for acl in entity.project.assignments:
                if acl.child_id in self.context_ids:
                    permissions = set(list(acl.rights))
                    if permissions.issubset(rights):
                        continue
                    for right in permissions:
                        rights.add(right)
        return rights

    @property
    def debug(self):
        return BLOBEntityAccessManager.__DebugOn__

class FolderAccessManager(BLOBEntityAccessManager):
    #TODO: Implement!
    __entity__ = 'Folder'

    def __init__(self, ctx):
        if (BLOBEntityAccessManager.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            BLOBEntityAccessManager.__DebugOn__ = sd.bool_for_default('OGoDocumentManagementDebugEnabled')
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for folder in objects:
            rights_set = self.project_rights(folder, set())
            rights[folder] = self.inherited_rights(folder, rights_set)
        if (self.debug):
            for k,v in rights.items():
                self.log.debug('Implied rights for {0} are {1}'.format(k, v))
        return rights


class FileAccessManager(BLOBEntityAccessManager):
    # Due to a stupid bug in early versions this access manager must register itself as procesing both
    # "Document" and "File" entities.  All the Logic commands use the document:: domain, but the entity
    # itself originally had a Coils entity name of "File"
    __entity__ = [ 'File', 'Document', 'Doc' ]

    def __init__(self, ctx):
        if (BLOBEntityAccessManager.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            BLOBEntityAccessManager.__DebugOn__ = sd.bool_for_default('OGoDocumentManagementDebugEnabled')
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for folder in objects:
            rights_set = self.project_rights(folder, set())
            rights[folder] = self.inherited_rights(folder, rights_set)
        if (self.debug):
            for k,v in rights.items():
                self.log.debug('Implied rights for {0} are {1}'.format(k, v))
        return rights
