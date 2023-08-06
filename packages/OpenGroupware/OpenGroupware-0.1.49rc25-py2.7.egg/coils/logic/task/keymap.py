#
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
#
COILS_TASK_KEYMAP = {
    'objectid':                 ['object_id', 'int', 0],
    'object_id':                ['object_id', 'int', 0],
    'parent_id':                ['parent_id', 'int', 0],
    'parentid':                 ['parent_id', 'int', 0],
    'parenttaskobjectid':       ['parent_id', 'int', 0],
    'parentobjectid':           ['parent_id', 'int', 0],
    'owner_id':                 ['owner_id', 'int', 0],
    'ownerid':                  ['owner_id', 'int', 0],
    'ownerobjectid':            ['owner_id', 'int', 0],
    'executor_id':              ['executor_id', 'int', 0],
    'executorid':               ['executor_id', 'int', 0],
    'executant_id':             ['executor_id', 'int', 0],
    'executantid':              ['executor_id', 'int', 0],
    'executantobjectid':        ['executor_id', 'int', 0],
    'executorobjectid':         ['executor_id', 'int', 0],
    'projectobjectid':          ['project_id', 'int', 0],
    'objectprojectid':          ['project_id', 'int', 0],
    'projectid':                ['project_id', 'int', 0],
    'project_id':               ['project_id', 'int', 0],
    'start':                    ['start', 'date'],
    'startdate':                ['start', 'date'],
    'end':                      ['end', 'date'],
    'enddate':                  ['end', 'date'],
    'kind':                     ['kind'],
    'type':                     ['kind'],
    'title':                    ['name'],
    'name':                     ['name'],
    'keywords':                 ['keywords'],
    'comment':                  ['comment'],
    'sensitivity':              ['sensitivity', 'int', 0],
    'priority':                 ['priority', 'int', 0],
    'complete':                 ['complete', 'int', 0],
    'percent_complete':         ['complete', 'int', 0],
    'percentcomplete':          ['complete', 'int', 0],
    'actual':                   ['actual_work'],
    'total':                    ['total_work'],
    'accounting':               ['accounting_info'],
    'travel':                   ['kilometers'],
    'companies':                ['associated_companies'],
    'contacts':                 ['associated_contacts'],
    'category':                 ['category'],
    'categories':               ['category'],
    'completiondate':           None,
    'completion_date':          None,
    'completed':                None,
    'status':                   None,
    'version':                  None,
    'objectVersion':            None,
    'job_status':               ['state'],
    'jobstatus':                ['state'],
    'state':                    ['state'],
    'acls':                     None,
    'logs':                     None,
    'modified':                 None,
    'graph':                    None
    }

COILS_COMMENT_KEYMAP = {
    'comment':                  ['comment'],
    'text':                     ['comment'],
    'taskobjectid':             ['task_id', 'int'],
    'task_id':                  ['task_id', 'int'],
    'taskid':                   ['task_id', 'int'],
    'job_id':                   ['task_id', 'int'],
    'jobid':                    ['task_id', 'int'],
    'action':                   ['action']
    }

