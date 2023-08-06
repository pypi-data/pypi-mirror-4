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
from sqlalchemy         import *
from coils.core         import *
from coils.core.logic   import GetCommand
from coils.foundation   import Project, Appointment, Contact, Enterprise
from coils.core.vcard   import Render
from utility            import read_cached_vcard, cache_vcard

class GetContactAsVCard(GetCommand):
    __domain__ = "contact"
    __operation__ = "get-as-vcard"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        self.objects = None
        self.object_ids = None
        if ('object' in params):
            self.mode = 1
            self.objects = [params['object']]
        elif ('objects' in params):
            self.mode = 2
            self.objects = params['objects']
        elif ('id' in params):
            self.mode = 1
            self.object_ids = [params['id']]
        elif ('ids' in params):
            self.mode = 2
            self.object_ids = params['ids']

    def run(self):
        if ((self.objects is None) and (self.object_ids is not None)):
            try:
                data = self._ctx.run_command("contact::get", ids=self.object_ids,
                                                             access_check=self.access_check)
            except Exception, e:
                self.log.exception('exception retrieving contact')
                self._result = None
                return
            self.objects = data
        if (self.objects is None):
            self._result = None
        else:
            self._result = []
            for contact in self.objects:
                vcf = read_cached_vcard(contact.object_id, contact.version)
                if (vcf is None):
                    vcf = Render.render(contact, self._ctx)
                    if (vcf is not None):
                        cache_vcard(contact.object_id, contact.version, vcf)
                if (vcf is not None):
                    self._result.append(vcf)
            if (self.mode == 1):
                if (len(self._result) > 0):
                    self._result = self._result[0]
                else:
                    self._result = None
        return