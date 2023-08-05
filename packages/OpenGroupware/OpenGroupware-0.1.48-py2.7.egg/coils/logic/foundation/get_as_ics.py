#
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
# 
from sqlalchemy             import *
from coils.core             import *
from coils.core.logic       import GetCommand
from coils.core.icalendar   import Render as ICalendar_Render
from coils.core.vcard       import Render as VCard_Render

def filename_for_ics(object_id, version, user_agent_id):
    id_string = str(object_id)
    prefix_a = id_string[-2:]
    prefix_b = id_string[-4:-2]
    return 'cache/ics/{0}/{1}/{2}.{3}.{4}.ics'.format(prefix_a, prefix_b, object_id, version, user_agent_id)


def is_ics_cached(object_id, version, user_agent_id):
    return BLOBManager.Exists(filename_for_ics(object_id, version, user_agent_id))


def read_cached_ics(object_id, version, user_agent_id):
    handle = BLOBManager.Open(filename_for_ics(object_id, version, user_agent_id), 'r')
    if (handle is None):
        return None
    # TODO: Do a nicer block read
    data = handle.read()
    BLOBManager.Close(handle)
    return data


def cache_ics(object_id, version, user_agent_id, ics):
    # TODO: Issue#127
    filename = filename_for_ics(object_id, version, user_agent_id)
    handle = BLOBManager.Create(filename.split('/'))
    handle.write(ics)
    handle.flush()
    BLOBManager.Close(handle)


class GetObjectAsICalendar(GetCommand):
    __domain__ = "object"
    __operation__ = "get-as-ics"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)
        self.disable_access_check()

    def parse_parameters(self, **params):
        if (params.has_key('object')):
            self.data = [params['object']]
            self.set_single_result_mode()
        elif (params.has_key('objects')):
            self.data = params['objects']
            self.set_multiple_result_mode()
        else:
            raise 'No objects provided to command.'

        self._use_cache = params.get('use_cache', True)

    def run(self):
        results = [ ]
        for entity in self.data:
            if self._use_cache:
                ics = read_cached_ics(entity.object_id, entity.version, self._ctx.user_agent_id)
            else:
                ics = None
            if (ics is None):
                if (isinstance(entity, Contact) or isinstance(entity, Enterprise) or isinstance(entity, Team)):
                    ics = VCard_Render.render(entity, self._ctx)
                else:
                    ics = ICalendar_Render.render(entity, self._ctx)
                if (ics is not None):
                    if (isinstance(ics, list)):
                        ics = ics[0]
                    self.log.debug('Caching ICS representation for objectId#{0} .'.format(entity.object_id))
                    cache_ics(entity.object_id, entity.version, self._ctx.user_agent_id, ics)
                    if entity.info:
                        if not (entity.info.file_size == len(ics) and entity.info.version == entity.version):
                            entity.info.update(entity, file_size=len(ics))
                            self._ctx.dirty()
            else:
                self.log.debug('Using cached ICS representation for objectId#{0}.'.format(entity.object_id))
            if (ics is not None):
                results.append(ics)
        self.set_return_value(results)
