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
from coils.core import EntityAccessManager

class AppointmentAccessManager(EntityAccessManager):
    __entity__ = 'appointment'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        # TODO: Implement
        #       Owner has full access
        #       Participants have read access
        #       Read access team has read access
        #       Write access teams have read/right access
        rights = { }
        for entity in objects:
            rights[entity] = set('l')
            if (entity.owner_id in self.context_ids):
                rights[entity].add('a') #admin (a)
                rights[entity].add('d') #delete (==w?)
                rights[entity].add('e') #edit
                rights[entity].add('u') #update (==w?)
                rights[entity].add('v') # ???
                rights[entity].add('r') # ???
            else:
                if (entity.access_id in self.context_ids):
                    rights[entity].add('r') # read (==v?)
                    rights[entity].add('v') # view
                if (entity.write_ids):
                    # Issue#135: 2011-01-28; fixed 2011-07-29
                    for object_id in [object_id for object_id in entity.write_ids.split(',')]:
                        if (object_id.isdigit()):
                            try:
                                object_id = int(object_id)
                            except:
                                self.log.error('Invalid objectId in Appoinment write list: "{0}"'.format(object_id))
                            else:
                                if (object_id in self.context_ids):
                                    rights[entity].add('d') # delete (==w?)
                                    rights[entity].add('e') # edit
                                    rights[entity].add('u') # update (==w?)
                                    rights[entity].add('v') # ???
                                    rights[entity].add('r') # ???
                                    rights[entity].add('w') # ???
                                    break
                for participant in entity.participants:
                    if (participant.participant_id is not None):
                        if (participant.participant_id in self.context_ids):
                            rights[entity].add('u') # update
                            rights[entity].add('v') # update
        return rights


class ResourceAccessManager(EntityAccessManager):
    __entity__ = 'resource'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set(self.default_rights())
        return rights
