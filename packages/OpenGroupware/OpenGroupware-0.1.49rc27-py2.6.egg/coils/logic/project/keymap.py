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
COILS_PROJECT_KEYMAP = {
    'objectid':             ['object_id', 'int', 0],
    'owner_id':             ['owner_id', 'int', 0],
    'parent_id':            ['parent_id', 'int', None],
    'parentid':             ['parent_id', 'int', None],
    'parentobjectid':       ['parent_id', 'int', None],
    'parentprojectid':      ['parent_id', 'int', None],
    'status':               ['status'],
    'comment':              ['comment'],
    'end':                  ['end', 'date', None],
    'kind':                 ['kind'],
    'name':                 ['name'],
    'title':                ['name'],
    'number':               ['number'],
    'is_fake':              ['is_fake', 'int', 0],
    'isfake':               ['is_fake', 'int', 0],
    'start':                ['start', 'date', None],
    'version':              ['version', 'int']
    }
