# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
import sys, time
import logging
from datetime    import datetime
from coils.foundation     import ObjectInfo, Appointment, ProjectAssignment, Participant, \
                         CompanyAssignment, Contact, Enterprise, Team, Project, \
                         Task, Team, Collection, CollectionAssignment, Route, \
                         Document, Process, Folder

COILS_TYPEMANAGER_CACHE = { }

class TypeManager:

    __slots__ = ('_log', '_orm', '_ctx')

    def __init__(self, ctx):
        self._ctx = ctx
        self._log =logging.getLogger("typemanager")
        self._orm = self._ctx.db_session()

    def check_cache(self, object_id):
        # Expire entries
        try:
            if (COILS_TYPEMANAGER_CACHE.has_key(object_id)):
                return COILS_TYPEMANAGER_CACHE[object_id][0]
        except TypeError, e:
            self._log.error('objectId was {0} = {1}'.format(type(object_id), object_id))
            self._log.exception(e)
        except Exception, e:
            self._log.exception(e)
        return None

    def purge_cache(self, object_id):
        if (COILS_TYPEMANAGER_CACHE.has_key(object_id)):
            del COILS_TYPEMANAGER_CACHE[object_id]

    def set_cache(self, object_id, kind):
        COILS_TYPEMANAGER_CACHE[object_id] = []
        COILS_TYPEMANAGER_CACHE[object_id].append(kind)
        COILS_TYPEMANAGER_CACHE[object_id].append(datetime.now())
        return kind

    @staticmethod
    def translate_kind_to_legacy(kind):
        return ObjectInfo.translate_kind_to_legacy(kind)

    @staticmethod
    def translate_kind_from_legacy(kind):
        return ObjectInfo.translate_kind_from_legacy(kind)

    def get_direntry(self, object_id):
        # TODO: Any possible way we can pre-cache the "file size"?

        class DirEntry(object):
            __slots__ = ('object_id', 'kind', 'display_name', 'file_name', 'size', 'owner', 'version')
            def __init__(self, object_id, kind, display_name, file_name, size, owner, version):
                self.object_id    = object_id
                self.kind         = kind
                self.display_name = display_name
                self.file_name    = file_name
                self.size         = size
                self.owner        = owner
                self.version      = owner

        query = self._orm.query(ObjectInfo).filter(ObjectInfo.object_id == object_id)
        data = query.all()
        if data:
            data = data[0]
            dentry = DirEntry(data.object_id, data.kind, data.display_name, None, 0, None, None)
        else:
            if self._ctx.amq_available:
                # If the Context is on the AMQ bus ask the administrator service to repair/review this
                # object-info entry.
                self._ctx.send(None, 'coils.administrator/repair_objinfo:{0}'.format(object_id), None)
            entity = self.get_entity(object_id)
            if entity:
                version      = entity.version if hasattr(entity, 'version') else 0
                display_name = entity.get_display_name() if hasattr(entity, 'get_display_name') else str(entity.object_id)
                file_name    = entity.get_file_name() if hasattr(entity, 'get_file_name') else '{0}.ics'.format(object_id)
                file_size    = 0
                owner_id     = entity.owner_id if hasattr(entity, 'owner_id') else None
                version      = entity.version if hasattr(entity, 'version') else 0
                return DirEntry(enity.object_id, entity.__entityName__, display_name, file_name, file_size, owner_id, version)
        return None

    def get_type(self, object_id, repair_enabled=True):
        # MEMOIZE ME!
        kind = self.check_cache(object_id)
        if (kind is None):
            query = self._orm.query(ObjectInfo).filter(ObjectInfo.object_id == object_id)
            data = query.all()
            if (len(data) == 0):
                kind = self.deep_search_for_type(object_id)
                self._log.debug('Deep search for objectId#{0} discovered type {1}'.format(object_id, kind))
                if ((kind != 'Unknown') and (self._ctx.amq_available)):
                    if repair_enabled:
                        self._log.debug('Requesting repair of ObjectInfo for objectId#{0}'.format(object_id))
                        self._ctx.send(None, 'coils.administrator/repair_objinfo:{0}'.format(object_id), None)
                    else:
                        # If repair_enabled is False, then someone disabled repair.  This is probably because
                        # we are doing a looking in order to do a repair.  If repair can generate repair
                        # requests then legitimately absent object references will create repair-loops that
                        # potentially never end.
                        self._log.debug('Repair of ObjectInfo is disabled [objectId#{0}]; loop prevention?'.format(object_id))
            elif (len(data) > 0):
                kind = str(data[0].kind)
        if (kind is None): return 'Unknown'
        self.set_cache(object_id, kind)
        return TypeManager.translate_kind_from_legacy(kind)

    def get_entity(self, object_id, repair_enabled=True):
        kind = self.get_type(object_id, repair_enabled=repair_enabled)
        # Since kind returned by get_type is a modern kind value, not a legecy kind value, we
        # we can use it to try to execute an implied Logic command
        if kind:
            if kind == 'Unknown':
                return None
            try:
                entity = self._ctx.run_command('{0}::get'.format(kind.lower()), id=object_id)
            except:
                return None
            else:
                return entity
        return None

    def get_entities(self, object_ids, limit = 0):
        entities = [ ]
        # Since the kine returned as the dict key is a modern kind value, not a legecy kind value, we
        # we can use it to try to execute an implied Logic commands
        for kind, ids in self._ctx.type_manager.group_ids_by_type(object_ids).items():
            try:
                result = self._ctx.run_command('{0}::get'.format(kind.lower()), ids=ids)
            except Exception as e:
                self._log.warn('attempt to use get_entities on unsupported object type "{0}"?'.format(kind))
                self._log.exception(e)
            else:
                entities.extend(result)
                if limit and len( entities ) > limit:
                    break
        return entities

    def get_display_name(self, object_id):
        data = query = self._orm.query(ObjectInfo).filter(ObjectInfo.object_id == object_id).all()
        if data:
            if data[0].display_name:
                return data[0].display_name
            entity = self.get_entity(object_id)
            if entity:
                if hasattr(entity, 'get_display_name'):
                    # Display names are limited to 127 characters
                    return entity.get_display_name()[0:127]
            return str(object_id)

    def filter_ids_by_type(self, object_ids, entity_name):
        groups = self.group_ids_by_type(object_ids)
        if (entity_name in groups):
            return groups[entity_name]
        return []

    def group_ids_by_type(self, object_ids):
        result = { }
        for object_id in object_ids:
            entity_name = self.get_type(object_id)
            if ( result.has_key(entity_name) ):
                result[entity_name].append(object_id)
            else:
                result[entity_name] = [ object_id ]
        return result

    def group_by_type(self, **params):
        if (params.has_key('objects')):
            return self._group_objects(params['objects'])
        elif (params.has_key('ids')):
            return self._group_ids(params['ids'])

    def _group_objects(self, entities):
        start = time.time()
        result = { }
        for entity in entities:
            if (entity is None):
                self._log.error('Encountered None entity while grouping objects')
            else:
                entity_name = entity.__entityName__
                if (result.has_key(entity_name)):
                    result[entity_name].append(entity)
                else:
                    result[entity_name] = [ entity ]
        end = time.time()
        self._log.debug('duration of grouping was %0.3fs' % (end - start))
        return result

    def _group_ids(self, object_ids):
        result = { }
        for object_id in object_ids:
            entity_name = self.get_type(object_id)
            if ( result.has_key(entity_name) ):
                result[entity_name].append(object_id)
            else:
                result[entity_name] = [ object_id ]
        return result

    def deep_search_for_type(self, object_id):
        #HACK: This entire method!
        # Types are: Appointment, Contact, Enterprise, participant (?), Project,
        #            Resource (?), Task,
        self._log.warn("Performing deep search for type of objectId#%s", object_id)
        # Appointment
        query = self._orm.query(Appointment).filter(Appointment.object_id == object_id)
        if (len(query.all()) > 0): return 'Date'
        # Contact
        query = self._orm.query(Contact).filter(Contact.object_id == object_id)
        if (len(query.all()) > 0): return 'Person'
        # Folder
        query = self._orm.query(Folder).filter(Folder.object_id == object_id)
        if (len(query.all()) > 0): return 'Folder'
        # Enterprise
        query = self._orm.query(Enterprise).filter(Enterprise.object_id == object_id)
        if (len(query.all()) > 0): return 'Enterprise'
        # participant
        query = self._orm.query(Participant).filter(Participant.object_id == object_id)
        if (len(query.all()) > 0): return 'DateCompanyAssignment'
        # Project
        query = self._orm.query(Project).filter(Project.object_id == object_id)
        if (len(query.all()) > 0): return 'Project'
        # Team
        query = self._orm.query(Team).filter(Team.object_id == object_id)
        if (len(query.all()) > 0): return  'Team'
        # Task
        query = self._orm.query(Task).filter(Task.object_id == object_id)
        if (len(query.all()) > 0): return 'Job'
        # Document
        query = self._orm.query(Document).filter(Document.object_id == object_id)
        if (len(query.all()) > 0): return 'Document'
        # Process
        query = self._orm.query(Process).filter(Process.object_id == object_id)
        if (len(query.all()) > 0): return 'Process'
        # Route
        query = self._orm.query(Route).filter(Route.object_id == object_id)
        if (len(query.all()) > 0): return 'Route'
        # Collection
        query = self._orm.query(Collection).filter(Collection.object_id == object_id)
        if (len(query.all()) > 0): return 'Collection'
        # CollectionAssignment
        query = self._orm.query(CollectionAssignment).filter(CollectionAssignment.object_id == object_id)
        if (len(query.all()) > 0): return 'collectionAssignment'
        # Hit the bottom!
        self._log.warn("Deep search failed to find type for objectId#%s", object_id)
        return None
