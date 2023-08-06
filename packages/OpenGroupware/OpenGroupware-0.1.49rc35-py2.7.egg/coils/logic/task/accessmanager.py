#!/usr/bin/python
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import EntityAccessManager

class TaskAccessManager(EntityAccessManager):
    __entity__ = 'Task'

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        cache = { }
        for entity in objects:
            rights[entity] = set()
            # TODO: Support team editor role
            # TODO: Should the creator have any implicit rights?
            if (self._ctx.is_admin):
                rights[entity].add('w') # Modify
                rights[entity].add('d') # Delete
                rights[entity].add('t') # Delete member
                rights[entity].add('r') # Read
                rights[entity].add('l') # List
                rights[entity].add('v') # View
            elif (entity.owner_id in self.context_ids):
                rights[entity].add('w') # Modify
                rights[entity].add('d') # Delete
                rights[entity].add('t') # Delete member
                rights[entity].add('r') # Read
                rights[entity].add('l') # List
                rights[entity].add('v') # View
            elif (entity.executor_id in self.context_ids):
                rights[entity].add('w') # Modify
                rights[entity].add('r') # Read
                rights[entity].add('l') # List
                rights[entity].add('v') # View

            if (entity.project_id is not None):
                # TODO: Rights inherited from project
                if (entity.project is not None):
                    if entity.project.object_id in cache:
                        for right in cache[entity.project.object_id]:
                            rights[entity].add(right)
                    else:
                        cache[entity.project.object_id] = set()
                        for right in self._ctx.access_manager.access_rights(entity.project, contexts=self.context_ids):
                            rights[entity].add(right)
                            cache[entity.project.object_id].add(right)

        return rights