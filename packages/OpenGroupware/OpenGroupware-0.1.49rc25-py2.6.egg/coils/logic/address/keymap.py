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
COILS_ADDRESS_KEYMAP = {
    'objectid':             ['object_id', 'int', 0],
    'object_id':            ['object_id', 'int', 0],
    'zip':                  ['postal_code'],
    'zip_code':             ['postal_code'],
    'postalcode':           ['postal_code'],
    'state':                ['province'],
    'type':                 ['kind'],
    'companyobjectid':      ['parent_id', 'int', 0],
    'company_id':           ['parent_id', 'int', 0],
    'companyid':            ['parent_id', 'int', 0],
    'enterprise_id':        ['parent_id', 'int', 0],
    'enterpriseid':         ['parent_id', 'int', 0],
    'parent_id':            ['parent_id', 'int', 0],
    'parentid':             ['parent_id', 'int', 0],
    }

COILS_TELEPHONE_KEYMAP = {
    'objectid':             ['object_id', 'int', 0],
    'object_id':            ['object_id', 'int', 0],
    'type':                 ['kind'],
    'companyobjectid':      ['parent_id', 'int', 0],
    'company_id':           ['parent_id', 'int', 0],
    'companyid':            ['parent_id', 'int', 0],
    'enterprise_id':        ['parent_id', 'int', 0],
    'enterpriseid':         ['parent_id', 'int', 0],
    'parent_id':            ['parent_id', 'int', 0],
    'parentid':             ['parent_id', 'int', 0],
    'number':               ['number', 'str'],
    }

COILS_COMPANY_COMMENT_KEYMAP ={
    'objectid':             ['object_id', 'int', 0],
    'object_id':            ['object_id', 'int', 0],
    'companyobjectid':      ['parent_id', 'int', 0],
    'company_id':           ['parent_id', 'int', 0],
    'companyid':            ['parent_id', 'int', 0],
    'enterprise_id':        ['parent_id', 'int', 0],
    'enterpriseid':         ['parent_id', 'int', 0],
    'parent_id':            ['parent_id', 'int', 0],
    'parentid':             ['parent_id', 'int', 0],
    }
    
COILS_COMPANYVALUE_KEYMAP = {
    'label':                ['label', 'str'],
    'widget':               ['widget', 'int'],
    'type':                 ['widget', 'int'],
    'uid':                  ['uid', 'int', None]
    }
    
