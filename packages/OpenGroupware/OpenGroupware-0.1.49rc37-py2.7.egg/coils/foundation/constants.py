#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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

'''
This role should grant the same privilages to a user as is owned by
the "ogo" account [context objectId#10000].  This allows the user to
do things like promote contacts to users, manage team membership,
delete anything, etc...
'''
OGO_ROLE_SYSTEM_ADMIN        = 1010000

'''
This role allows a user extended privileges relating to task entities,
such as being able to create/modify a task to have an owner other than
the creator or themselves.
'''
OGO_ROLE_HELPDESK            = 2010000

'''
Provides extensive powers over the OIE workflow components.  This includes
acces to all processes and routes.  The ability to place administrative
holds on processes and routes.
'''
OGO_ROLE_WORKFLOW_ADMIN      = 3010000

'''
Provides the ability to create new routes, temaples, formats, and schema
documents. Allows formats, templates, and schemas to be modified and/or
deleted.
'''
OGO_ROLE_WORKFLOW_DEVELOPERS = 3100000

'''
Provides the ability to perform list actions and other related data
extractions.  The primary purpose of this role is to limit the
ability to perform bulk-data exports and changes to some subset of
users.
'''
OGO_ROLE_DATA_MANAGER = 4010000
