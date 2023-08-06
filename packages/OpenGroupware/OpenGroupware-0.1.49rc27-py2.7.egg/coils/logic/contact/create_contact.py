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
from coils.core          import *
from coils.foundation    import *
from coils.logic.address import CreateCompany
from keymap              import COILS_CONTACT_KEYMAP
from command             import ContactCommand

class CreateContact(CreateCompany, ContactCommand):
    __domain__ = "contact"
    __operation__ = "new"

    def __init__(self):
        CreateCompany.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap =  COILS_CONTACT_KEYMAP
        self.entity = Contact
        CreateCompany.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCompany.parse_parameters(self, **params)

    def run(self):
        CreateCompany.run(self)
        self.set_enterprises()
        self.set_projects()
        self.save()
