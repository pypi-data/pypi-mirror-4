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
# THE SOFTWARE.
#
from coils.core          import *
from api                 import HordeAPI

class HordeGroupAPI(HordeAPI):

    def api_group_exists(self, args):
        team = self.context.run_command('team::get', id = args[0])
        if team is None:
            return False
        return True

    def api_group_getname(self, args):
        team = self.context.run_command('team::get', id = args[0])
        if team is None:
            return None
        return team.name

    def api_group_getdata(self, args):
        ''' Return: { id ->  { name, email, users } } '''
        result = { }
        team = self.context.run_command('team::get', id = args[0])
        if team is None:
            return None
        return { 'name': team.name,
                 'email': team.email,
                 'users': self.context.run_command('team::get-logins', team=team) }

    def api_group_listall(self, args):
        if (len(args)):
            account = self.context.run_command('account::get', login=args[0])
            if (account is not None):
                teams = self.context.run_command('team::get', member_id=account.object_id)
            else:
                teams = [ ]
        else:
            teams = self.context.run_command('team::list')
        result = { }
        for team in teams:
            result[team.object_id] = team.name
        return result

    def api_group_listusers(self, args):
        team = self.context.run_command('team::get', id = args[0])
        if team is None:
            return [ ]
        else:
            return self.context.run_command('team::get-logins', team=team)

    def api_group_listgroups(self, args):
        account = self.context.run_command('account::get', login=args[0])
        if (account is not None):
            teams = self.context.run_command('team::get', member_id=account.object_id)
        else:
            teams = [ ]
        result = { }
        for team in teams:
            result[team.object_id] = team.name
        return result

    def api_group_search(self, args):
        criteria = [ { 'key': 'name', 'expression': 'ILIKE', 'value': '%{0}%'.format(args[0]) } ]
        result = { }
        for team in self.context.run_command('team::search', criteria=criteria):
            result[team.object_id] = team.name
        return result
