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
# THE SOFTWARE.
#
from xml.dom    import minidom
from pytz       import timezone
from datetime   import datetime
from namespaces import XML_NAMESPACE, ALL_PROPS
from report     import Report

'''
    <?xml version="1.0" encoding="utf-8"?>
    <D:principal-match xmlns:D="DAV:">
        <D:principal-property><D:owner /></D:principal-property>
        <D:prop>
            <D:displayname />
            <schedule-inbox-URL xmlns="urn:ietf:params:xml:ns:caldav" />
            <schedule-outbox-URL xmlns="urn:ietf:params:xml:ns:caldav" />
            <calendar-user-address-set xmlns="urn:ietf:params:xml:ns:caldav" />
            <default-calendar-URL xmlns="http://icewarp.com/ns/" />
            <default-tasks-URL xmlns="http://icewarp.com/ns/" />
            <default-contacts-URL xmlns="http://icewarp.com/ns/" />
            <calendar-home-set xmlns="urn:ietf:params:xml:ns:caldav" />
            <addressbook-home-set xmlns="urn:ietf:params:xml:ns:carddav" />
        </D:prop>
    </D:principal-match>
'''

class webdav_principal_match(Report):

    def __init__(self, document, user_agent_description):
        Report.__init__(self, document, user_agent_description)

    @property
    def report_name(self):
        return 'principal-match'

    @property
    def parameters(self):
        _params = {}
        return self._params

    @property
    def command(self):
        return ''
