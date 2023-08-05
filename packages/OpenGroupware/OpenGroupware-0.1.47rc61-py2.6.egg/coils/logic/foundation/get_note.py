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

class GetNote(GetCommand):
    __domain__ = "note"
    __operation__ = "get"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)
        if ('uid' in params):
            self._caldav_uid = unicode(params.get('uid'))
        else:
            self._caldav_uid = None

    def add_comments(self, notes):
        # TODO: Can we get all the handles at once?
        self.log.info('getting comments')
        for note in notes:
            handle = self._ctx.run_command('note::get-handle', id=note.object_id)
            # TODO: Do a nicer block read
            note.content = handle.read()
        return notes

    def run(self):
        db = self._ctx.db_session()
        if (self._caldav_uid is None):
            query = db.query(Note).filter(and_(Note.object_id.in_(self.object_ids),
                                                Note.status != 'archived'))
        else:
            self.set_single_result_mode()
            query = db.query(Note).filter(Note.caldav_uid == self._caldav_uid)
        self.set_return_value(self.add_comments(query.all()))
