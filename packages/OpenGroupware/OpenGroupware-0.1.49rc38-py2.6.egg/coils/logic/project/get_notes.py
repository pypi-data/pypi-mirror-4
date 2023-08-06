#!/usr/bin/python
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
import traceback
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand

class GetProjectNotes(GetCommand):
    __domain__ = "project"
    __operation__ = "get-notes"

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        if ('id' in params):
            self.project_id = int(params['id'])
        elif ('project' in params):
            self.project_id = params['project'].object_id
        else:
            raise CoilsException('No project or project id provided to project::get-notes')

    def add_comments(self, notes):
        # TODO: Can we get all the handles at once?
        for note in notes:
            handle = self._ctx.run_command('note::get-handle', id=note.object_id)
            # TODO: Do a nicer block read
            # TODO: Notify administrator in case of a UnicodeDecodeError
            try:
                note.content = handle.read()
            except UnicodeDecodeError as e:
                message = traceback.format_exc()
                if (self._ctx.amq_available):
                    self._ctx.send_administrative_notice(
                        category='data',
                        urgency=6,
                        subject='UTF-8 Decoding Error with Note objectId#{0}'.format(note.object_id),
                        message=message)
                raise e
        return notes

    def run(self, **params):
        self.access_check = False
        self.mode = RETRIEVAL_MODE_MULTIPLE
        db = self._ctx.db_session()
        query = db.query(Note).filter(and_(Note.project_id==self.project_id,
                                            Note.status != 'archived'))
        return self.set_return_value(self.add_comments(query.all()))
