#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from sqlalchemy       import *
from coils.core       import *
from command          import ContactCommand


class AddContactNote(Command, ContactCommand):
    __domain__      = "contact"
    __operation__   = "new-note"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        if ('contact' in params): self._contact = params.get('contact')
        elif ('contact_id' in params):
            contact_id = int(params.get('contact_id'))
            self._contact = self.get_by_id(contact_id, self.access_check)
            if (self._contact is None):
                raise CoilsException('Specified ContactId#{0} not available for contact::new-note'.format(contact_id))
        else:
            raise CoilsException('No contact specified for contact::new-note')
        self._text = params.get('text', '')
        self._kind = params.get('kind', None)
        self._title = params.get('title', '')

    def run(self):
        # TODO: Check access to contact_id
        self.set_return_value(self._ctx.run_command('note::new', values={ 'title': self._title },
                                                                 text = self._text,
                                                                 kind = self._kind,
                                                                 context = self._contact))

