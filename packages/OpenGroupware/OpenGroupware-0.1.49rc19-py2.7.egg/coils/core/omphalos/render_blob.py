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

def render_file(entity, detail, ctx, favorite_ids=None):
    """ {'attachment': '/var/lib/opengroupware.org/documents/844500/14247000/14247521.xls',
         'creation': <DateTime '20100420T21:16:02' at 7f972fdc7ea8>,
         'creatorObjectId': 54720,
         'entityName': 'File',
         'fileSize': 604160,
         'fileType': 'xls',
         'filename': 'HAV fix 0410',
         'folderObjectId': 844520,
         'lastModified': <DateTime '20100420T21:16:02' at 7f972fdc7e60>,
         'objectId': 14247521,
         'ownerObjectId': 54720,
         'projectObjectId': 844500,
         'status': 'released',
         'title': 'v616 FK fix 0410',
         'version': 1} """

    blob = { 'entityName':      'File',
             'creation':        as_datetime(entity.created),
             'creatorObjectId': as_integer(entity.creator_id),
             'fileSize':        as_integer(entity.file_size),
             'fileType':        as_string(entity.extension),
             'filename':        as_string(entity.name),
             'folderObjectId':  as_integer(entity.folder_id),
             'lastModified':    as_datetime(entity.modified),
             'objectId':        as_integer(entity.object_id),
             'ownerObjectId':   as_integer(entity.owner_id),
             'projectObjectId': as_integer(entity.project_id),
             'status':          as_string(entity.status),
             'title':           as_string(entity.abstract),
             'version':         as_integer(entity.version) }
    return render_object(blob, entity, detail, ctx)


def render_folder(entity, detail, ctx, favorite_ids=None):
    """ { 'creation': <DateTime '20100414T13:01:13' at 7f972f740c68>,
          'creatorObjectId': 10100,
          'entityName': 'Folder',
          'folderObjectId': 844520,
          'objectId': 14216643,
          'ownerObjectId': 10100,
          'projectObjectId': 844500,
          'title': '201004'} """

    folder = { 'entityName':      'Folder',
               'creation':        as_datetime(entity.created),
               'creatorObjectId': as_integer(entity.creator_id),
               'folderObjectId':  as_integer(entity.folder_id),
               'objectId':        as_integer(entity.object_id),
               'ownerObjectId':   as_integer(entity.owner_id),
               'projectObjectId': as_integer(entity.project_id),
               'title':           as_string(entity.name) }
    if (detail & 16384):
        folder['_CONTENTS'] = [ ]
        contents = ctx.run_command('folder::ls', id=entity.object_id)
        for obj in contents:
            if (obj.__entityName__ == 'Document'):
                folder['_CONTENTS'].append(render_file(obj, 0, ctx))
            elif (obj.__entityName__ == 'Folder'):
                folder['_CONTENTS'].append(render_folder(obj, 0, ctx))
    return render_object(folder, entity, detail, ctx)
