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
from sqlalchemy import *
from coils.core import *
from coils.core.logic import GetCommand

class ListFolder(GetCommand):
    __domain__ = "folder"
    __operation__ = "ls"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if (len(self.object_ids) == 0):
            if ('folder' in params):
                # TODO: Test that the reference value is actually a folder entity
                self.object_ids.append(params['folder'].object_id)
            else:
                raise CoilsException('No folder specified to list')
        self._name = params.get('name', None)

    def run(self):
        db = self._ctx.db_session()
        self.set_multiple_result_mode()
        contents = [ ]
        if (self._name is None):
            query = db.query(Document).filter(and_(Document.folder_id.in_(self.object_ids),
                                                    Folder.status != 'archived'))
        else:
            filename = '.'.join(self._name.split('.')[:-1])
            extension = self._name.split('.')[-1:][0]
            query = db.query(Document).filter(and_(Document.folder_id.in_(self.object_ids),
                                                    Document.name == filename,
                                                    Document.extension == extension,
                                                    Document.status != 'archived'))
        result = query.all()
        contents.extend(result)
        if (self._name is None):
            query = db.query(Folder).filter(and_(Folder.folder_id.in_(self.object_ids),
                                                  Folder.status != 'archived'))
        else:
            query = db.query(Folder).filter(and_(Folder.folder_id.in_(self.object_ids),
                                                  Folder.name == self._name,
                                                  Folder.status != 'archived'))
        result = query.all()
        contents.extend(result)
        self.set_return_value(contents)
