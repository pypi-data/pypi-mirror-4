# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.foundation import KVC, ProjectAssignment

class ProjectCommand(object):

    def get_by_id(self, object_id, access_check):
        return self._ctx.run_command('project::get', id=object_id,
                                                      access_check=access_check)

    def set_assignment_acls(self):
        acls = KVC.subvalues_for_key(self.values, ['_ACCESS', '_ACLS', 'acls'])
        if acls:
            self._ctx.run_command('object::set-access', object=self.obj, acls=acls)


    def set_contacts(self):
        ''' [ {'entityName': 'assignment',
               'objectId': 10634162,
               'sourceEntityName': 'Project',
               'sourceObjectId': 10290,
               'targetEntityName': 'Contact',
               'targetObjectId': 10100}] '''
        assignments = KVC.subvalues_for_key(self.values,
                                            ['_CONTACTS', 'contacts'],
                                            default=None)
        if (assignments is not None):
            _ids = []
            for a in assignments:
                _id = a.get('targetObjectId', a.get('childId', None))
                if (_id is not None):
                    _ids.append(_id)
            self._ctx.run_command('project::set-contacts', project=self.obj, contact_ids=_ids)

    def set_enterprises(self):
        ''' [ {'entityName': 'assignment',
               'objectId': 10634162,
               'sourceEntityName': 'Project',
               'sourceObjectId': 10290,
               'targetEntityName': 'Enterprise',
               'targetObjectId': 10100}] '''
        assignments = KVC.subvalues_for_key(self.values,
                                            ['_ENTERPRISES', 'enterprises'],
                                            default=None)
        if assignments:
            _ids = []
            for a in assignments:
                _id = a.get('targetObjectId', a.get('childId', None))
                if (_id is not None):
                    _ids.append(_id)
            self._ctx.run_command('project::set-enterprises', project=self.obj, enterprise_ids=_ids)

    def purge_assignments(self):
        db = self._ctx.db_session()
        # TODO: Just do a delete, this is extra leg-work
        query = db.query(ProjectAssignment).filter(ProjectAssignment.parent_id == self.obj.object_id)
        for assignment in query.all():
            db.delete(assignment)
        
        
