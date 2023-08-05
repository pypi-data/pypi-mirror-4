#
# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from create_task       import CreateTask        # task::new
from update_task       import UpdateTask        # task::set
from delete_task       import DeleteTask        # task::delete
from get               import GetTask           # task::get
from get_todo          import GetToDoList       # task::get-todo
from get_archived      import GetArchivedList   # task::get-archived
from get_delegated     import GetDelegatedList  # task::get-delegated
from get_current       import GetCurrentList    # task::get-current
from comment           import CreateComment     # task::comment
from search            import SearchTasks       # task::search
from batch_archive     import BatchArchive      # task::batch-archive
from getgraph          import GetGraph           # task::get-graph
#from get_task_as_vtodo import GetTaskAsVToDo    # task::get-as-vtodo
from accessmanager     import TaskAccessManager
from tko               import TKOService

