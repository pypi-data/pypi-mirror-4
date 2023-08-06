#
# Copyright (c) 2010, 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
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
COILS_ACL_KEYMAP = {
    'object_id':        [ 'object_id', 'int', 0],
    'objectid':         [ 'object_id', 'int', 0],
    'parent_id':        [ 'parent_id', 'int', 0],
    'parentid':         [ 'parent_id', 'int', 0],
    'sourceobjectid':   [ 'parent_id', 'int', 0],
    'target_id':        [ 'target_id', 'int', 0],
    'context_id':       [ 'target_id', 'int', 0],
    'targetobjectid':   [ 'target_id', 'int', 0],
    'child_id':         [ 'target_id', 'int', 0],
    'childid':          [ 'target_id', 'int', 0],
    'projectid':          [ 'project_id', 'int', 0],
    'permissions':      [ 'operations', 'str', ''],
    'action':           [ 'action', 'str', 'allowed'],
    }

COILS_COLLECTION_KEYMAP = {
    'object_id':          [ 'object_id',  'int', 0],
    'objectid':           [ 'object_id',  'int', 0],
    'parentid':           [ 'project_id', 'int', 0],
    'parenttaskobjectid': [ 'project_id', 'int', 0],
    'parentobjectid':     [ 'project_id', 'int', 0],
    'projectid':          [ 'project_id', 'int', 0],
    'project_id':         [ 'project_id', 'int', 0],
    'dav_enabled':        [ 'dav_enabled', 'int'],
    'davenabled':         [ 'dav_enabled', 'int', 0],
    'auth_token':         [ 'auth_token', 'str', 'unpublished'],
    'otp':                [ 'auth_token', 'str', 'unpublished'],
    'projectobjectid':    [ 'project_id', 'int', 0],
    'kind':               [ 'kind',       'str', ''],
    'title':              [ 'title',      'str', ''],
    'name':               [ 'title',      'str', ''],
    'comment':            [ 'comment',    'str', '']
    }

COILS_COLLECTION_ASSIGNMENT_KEYMAP = {
    'collection_id':      [ 'collection_id', 'int', 0],
    'parentid':           [ 'collection_id', 'int', 0],
    'parent_id':          [ 'collection_id', 'int', 0],
    'collectionid':       [ 'collection_id', 'int', 0],
    'collectionobjectid': [ 'collection_id', 'int', 0],
    'assigned_id':        [ 'assigned_id',   'int', 0],
    'assignedid':         [ 'assigned_id',   'int', 0],
    'assignedobjectid':   [ 'assigned_id',   'int', 0],
    'sort_key':           [ 'sort_key',      'int', 0],
    'sortkey':            [ 'sort_key',      'int', 0]
    }

COILS_ATTACHMENT_KEYMAP = {
    'relatedid':          [ 'related_id', 'int', 0],
    'related_id':         [ 'related_id', 'int', 0],
    'webdav_uid':         [ 'webdav_uid', 'str', 0],
    'webdavuid':          [ 'webdav_uid', 'str', 0],
    'name':               [ 'webdav_uid', 'str', 0],
    'mimetype':           [ 'mimetype',   'str', 'application/octet-stream']
    }

COILS_OBJECTLINK_KEYMAP ={
    'objectid':             ['object_id', 'int', 0],
    'object_id':            ['object_id', 'int', 0],
    'targetobjectid':       ['target_id', 'int', 0],
    'target_id':            ['target_id', 'int', 0],
    'targetid':             ['target_id', 'int', 0],
    'sourceobjectid':       ['source_id', 'int', 0],
    'source_id':            ['source_id', 'int', 0],
    'sourceid':             ['source_id', 'int', 0],
    'label':                ['label', 'str', None],
    'type':                 ['kind', 'str', None],
    'kind':                 ['kind', 'str', None],
    }

COILS_NOTE_KEYMAP = {
    'entityname':               None,
    'title':                    ['name', 'str'],
    'title':                    ['title', 'str'],
    'content':                  ['content', 'str', ''],
    'text':                     ['content', 'str', ''],
    'data':                     ['content', 'str', ''],
    'categories':               ['categories', 'str', ''],
    'category':                 ['categories', 'str', ''],
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
