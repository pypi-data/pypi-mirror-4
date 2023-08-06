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
from pytz               import timezone
from datetime           import datetime, timedelta
from time               import time
from coils.core         import *
from coils.core.logic   import CreateCommand
from keymap             import COILS_PROJECT_KEYMAP
from command            import ProjectCommand

class CreateProject(CreateCommand, ProjectCommand):
    __domain__    = "project"
    __operation__ = "new"

    def prepare(self, ctx, **params):
        self.keymap = COILS_PROJECT_KEYMAP
        self.entity = Project
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)

    def fill_missing_values(self):
        if (self.obj.start is None):
            self.obj.start = datetime.now()
        if (self.obj.end is None):
            self.obj.end = datetime(2032, 12, 31, 18, 59, 59)
        if (self.obj.sky_url is None):
            # TODO: This should default to something meaningful
            pass
        if (self.obj.is_fake is None):
            self.obj.is_fake = 0

    def run(self):
        CreateCommand.run(self)
        self.fill_missing_values()
        self.set_contacts()
        self.set_enterprises()
        self.set_assignment_acls()
        self.obj.status = 'inserted'
        self.save()
        if (self.obj.number is None):
            self.obj.number = 'P{0}'.format(self.obj.object_id)
        #TODO: set modified
        folder = self._ctx.run_command('folder::new', values={ 'projectId': self.obj.object_id,
                                                               'name':      self.obj.number } )
        self.notify()
