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
from coils.core import EntityAccessManager

class CompanyAccessManager(EntityAccessManager):
    # TODO: Deal with globally available contacts
    #__entity__ = [ 'Contact', 'Enterprise' ]

    def __init__(self, ctx):
        EntityAccessManager.__init__(self, ctx)

    def implied_rights(self, objects):
        rights = { }
        for entity in objects:
            rights[entity] = set()
            if (entity.__entityName__ == 'Contact'):
                if (entity.is_account is not None):
                    if (entity.is_account == 1):
                        rights[entity].add('l')
                        rights[entity].add('r')
            if (entity.owner_id in self.context_ids):
                # Owner of a Contact or Enterprise gets full rights
                for right in list('lrwad'):
                    rights[entity].add(right)
            if (entity.object_id in self.context_ids):
                # A user has the rights to modify themselves!
                # While there may be teams in the context_ids but teams will never be checked here.
                for right in list('lrwad'):
                    rights[entity].add(right)
        return rights
