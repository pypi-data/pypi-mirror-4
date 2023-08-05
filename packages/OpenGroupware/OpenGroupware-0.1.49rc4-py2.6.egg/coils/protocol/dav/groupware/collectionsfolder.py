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
import hashlib
from coils.core                        import Collection
from coils.net                         import DAVFolder, \
                                              DAVObject, \
                                              DAVFolder, \
                                              EmptyFolder
from collectionfolder                  import CollectionFolder
from groupwarefolder import GroupwareFolder

class CollectionsFolder(DAVFolder, GroupwareFolder):

    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def _load_contents(self):
        content = self.context.run_command('collection::list', properties=[Collection])
        if (content is not None):
            for collection in content:
                if (collection.dav_enabled):
                    self.insert_child(collection.object_id, collection, alias=collection.title)
        else:
            return False
        return True

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
            if (self.has_child(name)):
                collection = self.get_child(name)
            else:
                collection = None
        else:
            collection = self.context.run_command('collection::get', name=name)
        if (collection is not None):
            if (collection.dav_enabled):
                return CollectionFolder(self, name,
                                        entity=collection,
                                        parameters=self.parameters,
                                        request=self.request,
                                        context=self.context)
        else:
            print 'Failed to load collection "{0}".'.format(name)
        self.no_such_path()

    #
    # MKCOL
    #

    def do_MKCOL(self, name):
        ''' Create a collection with the specified name. '''
           
        collection = self.context.run_command( 'collection::new', values = { 'name': name, 
                                                                             'davenabled': 1, } )
        self.context.commit()
        self.request.simple_response(201)

    #
    # MOVE
    #

    def do_MOVE(self, name):
        # See Issue#158
        # TODO: Support the Overwrite header T/F
        ''' MOVE /dav/Projects/Application%20-%20BIE/Documents/87031000 HTTP/1.1

            RESPONSE
               201 (Created) - Created a new resource
               204 (No Content) - Moved to an existing resource
               403 (Forbidden) - The source and destination URIs are the same.
               409 - Conflict
               412 - Precondition failed
               423 - Locked
               502 - Bad Gateway
            '''

        source, target, target_name, overwrite = self.move_helper(name)

        self.log.debug('Request to move "{0}" to "{1}" as "{2}".'.format(source, target, target_name))

        if isinstance(source.entity, Collection) and target == self:
            # We are renaming a colleciton to a different name
            # This is the only type of move supported in this context

            if overwrite:
				# TODO: Does this mean anything in this case? Probably not.
                #       If a project of the same number exists we are just
                #       going to error anyway.
				pass
            
            values = { 'name': target_name }
                                
            result = self.context.run_command('collection::set', object=source.entity,
                                                                 values=values)
            self.context.commit()
            self.request.simple_response(204)
            return
                
        raise CoilsException('Moving {0} via WebDAV is not supported'.format(source.entity))
