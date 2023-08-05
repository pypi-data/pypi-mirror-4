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
from coils.foundation import KVC

class EnterpriseCommand(object):

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('enterprise::get', id=object_id,
                                                      access_check=access_check)

    def set_contacts(self):
        ''' [ {'entityName': 'assignment',
               'objectId': 10634162,
               'sourceEntityName': 'Enterprise',
               'sourceObjectId': 10290,
               'targetEntityName': 'Contact',
               'targetObjectId': 10100}] '''
        # The targetObjectId is the contact id, how assignments are represented depends on thier
        # context; in a Contact entity the targetObjectId is the enterprise id. The source is the
        # entity being rendered.
        assignments = KVC.subvalues_for_key(self.values,
                                            ['_CONTACTS', 'contacts'],
                                            default=None)
        if (assignments is not None):
            _ids = []
            for a in assignments:
                _id = a.get('targetObjectId', a.get('childId', None))
                if (_id is not None):
                    _ids.append(_id)
            self._ctx.run_command('enterprise::set-contacts', enterprise=self.obj, contact_ids=_ids)
