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
from render_object import *

def render_collection(entity, detail, ctx):
    """ { 'creation': <DateTime '20100414T13:01:13' at 7f972f740c68>,
          'creatorObjectId': 10100,
          'entityName': 'Folder',
          'folderObjectId': 844520,
          'objectId': 14216643,
          'ownerObjectId': 10100,
          'projectObjectId': 844500,
          'title': '201004'} """
    collection = { 'entityName':      'Collection',
                   'objectId':        as_integer(entity.object_id),
                   'ownerObjectId':   as_integer(entity.owner_id),
                   'projectObjectId': as_integer(entity.project_id),
                   'comment':         as_string(entity.comment),
                   'kind':            as_string(entity.kind),
                   'version':         as_integer(entity.version),
                   'otp':             as_string(entity.auth_token),
                   'davEnabled':      as_integer(entity.dav_enabled),
                   'title':           as_string(entity.title) }
    if (detail & 128):
        tm = ctx.type_manager
        collection['_MEMBERSHIP'] = [ ]
        contents = ctx.run_command('collection::get-assignments', collection=entity)
        for obj in contents:
            collection['_MEMBERSHIP'].append( { 'entityName': 'collectionAssignment',
                                                'objectId': obj.object_id,
                                                'collectionObjectId': entity.object_id,
                                                'assignedObjectId': obj.assigned_id,
                                                'assignedEntityName': tm.get_type(obj.assigned_id),
                                                'sortKey': as_integer(obj.sort_key) } )
    return render_object(collection, entity, detail, ctx)
