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
from coils.core import *

class TeamCommand(object):

    def set_membership(self):
        ''' According to the zOGI Spec:
               Team entities are entirely read-only prior to r879 (2007-12-19). As of r879 the membership of a
               team can be adjusted via putObject assuming the user has sufficient permissions. Members of the
               team must be specified in the "memberObjectIds" attribute as an array of objectIds. '''
        if 'memberObjectIds' in self.values:
            # TODO: Grant this right to members of the 'team creators' team.
            if self._ctx.is_admin:
                member_ids = self.values['memberObjectIds']
                if isinstance(member_ids, basestring):
                    member_ids = [x.strip() for x in member_ids.split(',')]
                if isinstance(member_ids, list):
                    member_ids = [ int(x) for x in self.values['memberObjectIds'] ]
                    for member in self.obj.members:
                        if member.object_id in member_ids:
                            member_ids.remove(member.object_id)
                        else:
                            # Delete assignment from team
                            self._ctx.db_session().delete(member)
                    for member_id in member_ids:
                        self._ctx.db_session().add(CompanyAssignment(self.obj.object_id, member_id))
                else:
                    raiseCoilsException('Team membership must be specified as a list of object ids')
