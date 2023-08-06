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

class ContactCommand(object):

    def get_favorite_ids(self):
        return self._ctx.defaults_manager.default_as_list('person_favorites', [])

    def set_favorite_ids(self, favorite_ids):
        favorite_ids = [ int(x) for x in favorite_ids ];
        self._ctx.defaults_manager.set_default_value('person_favorites', favorite_ids)
        self._ctx.defaults_manager.sync()

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('contact::get', id=object_id,
                                                      access_check=access_check)

    def set_enterprises(self):
        ''' [ { 'entityName': 'assignment',
               'objectId': 12740176,
               'sourceEntityName': 'Contact',
               'sourceObjectId': 12740133,
               'targetEntityName': 'Enterprise',
               'targetObjectId': 12740110 } ] '''
        # The targetObjectId is the enterprise id, how assignments are represented depends on thier
        # context; in a Enterprise entity the targetObjectId is the contact id.  The source is the
        # entity being rendered.

        assignments = KVC.subvalues_for_key(self.values, ['_ENTERPRISES', 'enterprises'], default=None)
        if (assignments is not None):
            _ids = []
            for a in assignments:
                _id = a.get('targetObjectId', a.get('parentId', None))
                if (_id is not None):
                    _ids.append(int(_id))
            self._ctx.run_command('contact::set-enterprises', contact=self.obj, enterprise_ids=_ids)

    def set_projects(self):
        ''' [ { 'entityName': 'assignment',
                'objectId': 11400,
                'sourceEntityName': 'Contact',
                'sourceObjectId': 10100,
                'targetEntityName': 'Project',
                'targetObjectId': 11360} ] '''
        # Project assignments are wierd, the
        assignments = KVC.subvalues_for_key(self.values, ['_PROJECTS', 'projects'], default=None)
        if (assignments is not None):
            _ids = []
            for a in assignments:
                _id = a.get('targetObjectId', a.get('child_id', None))
                if (_id is not None):
                    _ids.append(int(_id))
            self._ctx.run_command('contact::set-projects', contact=self.obj, project_ids=_ids)
