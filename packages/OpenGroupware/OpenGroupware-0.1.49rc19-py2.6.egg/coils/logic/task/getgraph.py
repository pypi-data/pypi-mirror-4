#
# Copyright (c) 2010, 2011, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import *

class GetGraph(Command):
    # WARN: This is a performance critical command,  it gets invoked a lot.
    __domain__ = "task"
    __operation__ = "get-graph"
    root = None

    def __init__(self):
        Command.__init__(self)

    def _chase_root(self, task):
        if task.parent_id:
            query = self._ctx.db_session().query(Task).filter(Task.object_id == task.parent_id)
            query = query.enable_eagerloads(False)
            parent = query.all()
            if parent:
                return self._chase_root(parent[0])
            else:
                return task
        else:
            return task

    def _get_children(self, object_id):
        db = self._ctx.db_session()
        query = db.query(Task.object_id).filter(Task.parent_id == object_id)
        query = query.enable_eagerloads(False)
        return [ x[0] for x in query.all() ]

    def _get_graph(self, object_id):
        graph = { }
        children = self._get_children(object_id)
        for child in children:
            graph[str(child)] = self._get_graph(child)
        return graph

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.object_id = params.get('id', None)
        self.obj    = params.get('object', None)

    def run(self):
        db = self._ctx.db_session()
        if self.object_id:
            self.obj = self._ctx.run_command('task::get', id=[self._object_id])
        if not self.obj:
            raise COILSException(404, "No task available to command task::get-graph")
        root = self._chase_root(self.obj)
        self.set_result( { str(root.object_id) : self._get_graph(root.object_id) } )
