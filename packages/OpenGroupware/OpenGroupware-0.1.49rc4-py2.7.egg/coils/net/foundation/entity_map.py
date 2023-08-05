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
# THE SOFTWARE.
#

ENTITYMAP = { 'Contact':     { 'get-command'  : 'contact::get',
                               'data-command' : 'object::get-as-ics',
                               'mime-type'    : 'text/x-vcard' },
              'Appointment': { 'get-command'  : 'appointment::get',
                               'data-command' : 'object::get-as-ics',
                               'mime-type'    : 'text/calendar' },
              'Route':       { 'get-command'  : 'route::get',
                               'data-command' : 'route::get-text',
                               'mime-type'    : 'text/xml' },
              'Message':     { 'get-command'  : 'message::get',
                               'data-command' : 'message::get-text',
                               'mime-type'    : 'text/plain' },
              'Team':        { 'get-command'  : 'team::get',
                               'data-command' : 'team::get-as-ics',
                               'mime-type'    : 'text/x-vcard' },
              'Document':    { 'get-command'  : 'document::get',
                               'data-command' : 'document::get-handle',
                               'mime-type'    : 'application/octet-stream' },
              'note':        { 'get-command'  : 'note::get',
                               'data-command' : 'object::get-as-ics',
                               'mime-type'    : 'text/calendar' },
              'Process':     { 'get-command'  : 'process::get',
                               'data-command' : 'object::get-as-ics',
                               'mime-type'    : 'text/calendar' },
              'Task':        { 'get-command'  : 'task::get',
                               'data-command' : 'task::get-as-ics',
                               'mime-type'    : 'text/calendar' }
            }