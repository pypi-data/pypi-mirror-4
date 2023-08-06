#
# Copyright (c) 2009, 2011, 2012
# Adam Tauno Williams <awilliam@whitemice.org>
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

#TODO: This should really be moved to the useragent component of coils.core

# This is a dictionary used to convert XML namespace's into the "domains" that
# are used internally.
XML_NAMESPACE = { u'http://www.w3.org/1999/xhtml':                 u'xhtml',
                  u'dav':                                          u'webdav',
                  u'dav:':                                         u'webdav',
                  u'http://apache.org/dav/props/':                 u'webdav',
                  u'urn:schemas-microsoft-com:office:office':      u'msoffice',
                  u'urn:schemas-microsoft-com:office:word':        u'msword',
                  u'http://schemas.microsoft.com/hotmail/':        u'hotmail',
                  u'urn:schemas-microsoft-com:':                   u'mswebdav',
                  u'urn:schemas:httpmail:':                        u'mshttpmail',
                  u'http://schemas.microsoft.com/exchange/':       u'msexchange',
                  u'urn:schemas:calendar:':                        u'mscalendar',
                  u'urn:schemas:contacts:':                        u'mscontacts',
                  u'http://webdav.org/cadaver/custom-properties/': u'cadaver',
                  u'http://services.eazel.com/namespaces':         u'eazel', # Nautilus?
                  u'http://www.w3.org/2005/Atom':                  u'atom',
                  u'http://groupdav.org/':                         u'groupdav',
                  u'http://calendarserver.org/ns/':                u'caldav',
                  u'urn:ietf:params:xml:ns:caldav':                u'caldav',
                  u'urn:ietf:params:xml:ns:carddav':               u'carddav',
                  u'57c7fc84-3cea-417d-af54-b659eb87a046':         u'coils',
                  u'"http://ucb.openoffice.org/dav/props/':        u'openoffice',
                  u'http://icewarp.com/ns/':                       u'icewarp', }


REVERSE_XML_NAMESPACE = { 'webdav':                                u'dav',
                          'apache':                                u'http://apache.org/dav/props/',
                          'caldav':                                u'urn:ietf:params:xml:ns:caldav',
                          'carddav':                               u'urn:ietf:params:xml:ns:carddav',
                          'coils':                                 u'57c7fc84-3cea-417d-af54-b659eb87a046',
                          'groupdav':                              u'http://groupdav.org/',
                          'mswebdav':                              u'urn:schemas-microsoft-com',
                          'openoffice':                            u'"http://ucb.openoffice.org/dav/props/',
                          'atom':                                  u'http://www.w3.org/2005/Atom',
                          'icewarp':                               u'http://icewarp.com/ns/', }

ALL_PROPS = [('get_property_webdav_name',             u'DAV:', u'name',             u'webdav'),
             ('get_property_webdav_href',             u'DAV:', u'href',             u'webdav'),
             ('get_property_webdav_getcontenttype',   u'DAV:', u'getcontenttype',   u'webdav'),
             ('get_property_webdav_contentclass',     u'DAV:', u'contentclass',     u'webdav'),
             ('get_property_webdav_getlastmodified',  u'DAV:', u'getlastmodified',  u'webdav'),
             ('get_property_webdav_getcontentlength', u'DAV:', u'getcontentlength', u'webdav'),
             ('get_property_webdav_iscollection',     u'DAV:', u'iscollection',     u'webdav'),
             ('get_property_webdav_displayname',      u'DAV:', u'displayname',      u'webdav'),
             ('get_property_caldav_getctag',
                u'urn:ietf:params:xml:ns:caldav',              u'getctag',          u'webdav'),
             ('get_property_webdav_resourcetype',     u'DAV:', u'resourcetype',     u'webdav')]
