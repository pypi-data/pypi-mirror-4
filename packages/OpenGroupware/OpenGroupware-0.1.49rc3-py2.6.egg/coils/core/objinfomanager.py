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
#
import traceback, os
from typemanager               import TypeManager
from coils.foundation          import ObjectInfo, BLOBManager
from exception                 import CoilsException

KINDS_WITH_FILESIZE = ( 'Document', 'note', 'Note' )
KINDS_WITH_ICALENDAR = ( 'Contact', 'Enterprise', 'Team', 'Task', 'note', 'Note', 'Appointment')

class ObjectInfoManager(object):

    __slots__ = ( '_ctx', '_log', '_srv' )

    def __init__(self, ctx, log=None, service=None):
        self._ctx = ctx
        self._log = log
        self._srv = service

    @staticmethod
    def Repair(entity, ctx, log=None, service=None):
        om = ObjectInfoManager(ctx, log=log, service=service)
        if om.repair(entity=entity):
            ctx.dirty()
            return True
        return False

    def repair(self, object_id=None, entity=None):

        if object_id:
            # Attempt to get an entity via the type manager's get_entity short-cut
            # This requires a ::get command be implemented for the entity
            entity = self._ctx.type_manager.get_entity(object_id, repair_enabled=False)
        elif entity:
            if hasattr(entity, 'object_id'):
                object_id = entity.object_id
            else:
                # TODO: Should we log the attempt to repair an improper entity?
                return False
        else:
            if (object_id is None) and (entity is None):
                raise CoilsException('Either an "object_id" or an "entity" must be specified for ObjectInfo repair.')
            else:
                # Perhaps an objectId of zero was specified, this is a no-op.
                return False

        # Attempt to retrieve an existing ObjectInfo record for the objectd
        info = self._ctx.db_session().query(ObjectInfo).filter(ObjectInfo.object_id == object_id).all()
        if info:
            # ObjectInfo record exists
            info = info[0]
        else:
            # ObjectInfo record does not exist, create one
            # This will be a level 0 record initially, but may be promoted if the attempt
            # to retrieve the entity via the type managers get_entity method
            kind = self._ctx.type_manager.deep_search_for_type(object_id)
            if kind:
                if kind == 'Unknown':
                    # Was unable to discover the kind for this object id; possibly it is invalid?
                    # We cannot create an ObjectInfo Record
                    self._log.debug('Type of objectId#{0} not found.'.format(object_id))
                    return False
                else:
                    # We discovered the type, so we can create at least a level 0 info entry.
                    kind = TypeManager.translate_kind_to_legacy(kind)
                    info = ObjectInfo(object_id, kind)
                    self._ctx.db_session().add(info)
            else:
                return False

        if entity:
            # We successfully retrieved the entity, so we can upgrade the info entry
            try:
                ics_size  = None  # The size of the iCalendar representation, if any
                file_size = None  # The size of the 'raw' object contents
                if entity.__entityName__ in KINDS_WITH_FILESIZE:
                    file_size = entity.file_size
                    # HACK: Many databases contain Note entries where the file_size attribute is not set
                    #       This hack repairs that condition if it is encountered
                    if file_size is None and entity.__entityName__.lower() == 'note':
                        handle = self._ctx.run_command('note::get-handle', id=entity.object_id)
                        handle.stream.seek(0, os.SEEK_END)
                        entity.file_size = handle.tell()
                        file_size = entity.file_size
                        BLOBManager.Close(handle)
                else:
                    file_size = None
                if entity.__entityName__ in KINDS_WITH_ICALENDAR:
                    ics = self._ctx.run_command('object::get-as-ics', object=entity)
                    if ics:
                        ics_size = len(ics)
                info.update(entity, file_size=file_size, ics_size=ics_size)
            except UnicodeEncodeError:
                message = 'ObjectId:{0} ({1})\n\nError:{2}'.format(entity.object_id, entity.__entityName__, traceback.format_exc())
                if (self._ctx.amq_available):
                    self._ctx.send_administrative_notice(
                        category='data',
                        urgency=6,
                        subject='UnicodeEncodeError in ObjectInfo Repair',
                        message=message)
                if self._log:
                    self._log.error(message)
                return False
            except Exception, e:
                if self._log: self._log.exception(e)
                return False

        return True