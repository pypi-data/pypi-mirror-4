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
COILS_FOLDER_KEYMAP = {
    'entityname':               None,
    'name':                     ['title', 'str'],
    'name':                     ['name', 'str'],
    'objectid':                 ['object_id', 'int', 0],
    'object_id':                ['object_id', 'int', 0],
    'company_id':               ['company_id', 'int', None],
    'companyid':                ['company_id', 'int', None],
    'person_id':                ['company_id', 'int', None],
    'enterprise_id':            ['company_id', 'int', None],
    'parent_id':                ['folder_id', 'int', None],
    'parentid':                 ['folder_id', 'int', None],
    'parentobjectid':           ['folder_id', 'int', None],
    'folderid':                 ['folder_id', 'int', None],
    'folderobjectid':           ['folder_id', 'int', None],
    'projectid':                ['project_id', 'int', None],
    'project_id':               ['project_id', 'int', None],
    'projectobjectid':          ['project_id', 'int', None]
}

COILS_DOCUMENT_KEYMAP = {
    'entityname':               None,
    'title':                    ['name', 'str'],
    'title':                    ['title', 'str'],
    'extension':                ['extension', 'str'],
    'kind':                     ['extension', 'str'],
    'abstract':                 ['abstract', 'str'],
    'objectid':                 ['object_id', 'int', 0],
    'object_id':                ['object_id', 'int', 0],
    'company_id':               ['company_id', 'int', 0],
    'companyid':                ['company_id', 'int', 0],
    'companyobjectid':          ['company_id', 'int', 0],
    'person_id':                ['company_id', 'int', 0],
    'enterprise_id':            ['company_id', 'int', 0],
    'appointment_id':           ['appointment_id', 'int', 0],
    'appontmentid':             ['appointment_id', 'int', 0],
    'appointmentobjectid':      ['appointment_id', 'int', 0],
    'projectid':                ['project_id', 'int', 0],
    'project_id':               ['project_id', 'int', 0],
    'projectobjectid':          ['project_id', 'int', 0]
}
