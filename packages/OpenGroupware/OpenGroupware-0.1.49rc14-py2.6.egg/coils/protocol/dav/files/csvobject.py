#
# Copyright (c) 2010, 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
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
import hashlib, gc
from StringIO                          import StringIO
from coils.core                        import BLOBManager, Contact
from coils.net                         import DAVObject, CachedData

#
#  WARN: THis code is broken!
#
def none_to_empty(value):
    if (value is None):
        return ''
    return value


class CSVObject(DAVObject):
    def __init__(self, parent, name, **params):
        self.contents = None
        self._cached_object = None
        DAVObject.__init__(self, parent, name, **params)

    @property
    def cached_object(self):
        return self._cached_object

    def get_property_webdav_getcontenttype(self):
        return 'text/plain'

    def get_property_getetag(self):
        return self.ctag

    def get_property_webdav_getcontentlength(self):
        self.load_contents()
        return str(self.cached_object.size)

    def _load_contents(self):
        if self._cached_object is None:
            self._cached_object = CachedData(self.context.account_id, self.webdav_url, self.ctag)
            if (self.cached_object.not_current):
                self.log.debug('Cached representation of object is not current, loading contents')
                if (self.contents is None):
                    self.contents = self.context.run_command(self.command, properties=[Contact])
                stream = self._render_contact_list()
                self.cached_object.write_from_stream(stream)
                BLOBManager.Close(stream)
            else:
                self.log.debug('Cached representation of object is current.')
        return True

    def _render_contact_list(self):
        handle = BLOBManager.ScratchFile()
        self.log.debug('Generating CSV content of {0} entities'.format(len(self.contents)))
        start = self.context.get_timestamp()
        handle.write('objectId|firstName|lastName|department|'
                     'name1|name2|name3|street|postalCode|city|province|country|'
                     'homePhone|workPhone|officePhone|mobilePhone|faxPhone|'
                     'email|url|title|position|displayName\r\n')
        for contact in self.contents:
            mailing =  contact.addresses[ 'mailing' ]
            tel_home = none_to_empty(contact.telephones[ '05_tel_private' ] )
            tel_work = none_to_empty(contact.telephones[ '02_tel' ] )
            tel_off  = none_to_empty(contact.telephones[ '01_tel' ] )
            tel_cell = none_to_empty(contact.telephones[ '03_tel_funk' ] )
            tel_fax  = none_to_empty(contact.telephones[ '10_fax' ] )
            title    = none_to_empty(contact.companyvalues[ 'job_title'].string_value)
            position = none_to_empty(contact.companyvalues[ 'job_title1' ].string_value)
            handle.write('{0}|{1}|{2}|{3}|'.format(contact.object_id,
                                                   none_to_empty(contact.first_name),
                                                   none_to_empty(contact.last_name),
                                                   none_to_empty(contact.department)))
            if (mailing is not None):
                handle.write('{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|'.\
                    format(none_to_empty(mailing.name1), # name1 : 0
                           none_to_empty(mailing.name2), # name2 : 1
                           none_to_empty(mailing.name3), # name3 : 2
                           none_to_empty(mailing.street), # street : 3
                           none_to_empty(mailing.postal_code), # postalCode : 4
                           none_to_empty(mailing.city), # city : 5
                           none_to_empty(mailing.province), # province : 6
                           none_to_empty(mailing.country))) # country :7
            else:
                handle.write('|||||')
            # homePhone
            handle.write('{0}|{1}|{2}|{3}|{4}|'.format(none_to_empty(tel_home), # homePhone   : 0
                                                       none_to_empty(tel_work), # workPhone   : 1
                                                       none_to_empty(tel_off),  # officePhone : 2
                                                       none_to_empty(tel_cell), # mobilePhone : 3
                                                       none_to_empty(tel_fax))) # faxPhone    : 4
            # email
            email = contact.get_company_value_text('email1')
            if (email is None): email = contact.get_company_value_text('email2')
            if (email is None): email = contact.get_company_value_text('email3')
            handle.write('{0}|'.format(none_to_empty(email)))
            handle.write('{0}|'.format(none_to_empty(contact.URL))) # url
            handle.write('{0}|'.format(none_to_empty(title))) # title
            handle.write('{0}|'.format(none_to_empty(position))) # position
            handle.write('{0}|'.format(none_to_empty(contact.display_name))) # displayName
            handle.write('\r\n')
        end = self.context.get_timestamp()
        self.log.debug('Generation of CSV content consumed {0}s ({1}s per entry)'.format(end - start,
                                                                                         (end - start) / len(self.contents)))
        self.contents = None
        handle.seek(0)
        return handle

    def do_GET(self):
        if (self.load_contents()):
            self.request.stream_response(200,
                                         stream=self.cached_object.get_stream(),
                                         mimetype='text/plain',
                                         headers={ 'etag': self.ctag } )
            self.cached_object.close_cache()
            self.context.commit()
            self.context.db_session().expunge_all()
            print 'GC:{0}'.format(gc.collect())
            from coils.foundation.api.objgraph import get_most_common_types, by_type
            import pprint
            pprint.pprint(get_most_common_types())
