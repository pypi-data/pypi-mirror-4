#
# Copyright (c) 2009, 2012
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
from sqlalchemy     import *
from base           import Base, KVC
from company        import CompanyInfo, Telephone
from sqlalchemy.orm import relation,backref
from sqlalchemy.ext.associationproxy import association_proxy


def create_comment(x):
    print x
    return CompanyInfo()

class Contact(Base, KVC):
    """ An OpenGroupware Contact (Person) object """
    __tablename__        = 'person'
    __entityName__       = 'Contact'
    __internalName__     = 'Person'
    object_id            = Column("company_id",
                                  ForeignKey('log.object_id'),
                                  ForeignKey('object_acl.object_id'),
#                                  ForeignKey('telephone.company_id'),
                                  primary_key=True)
    owner_id         = Column("owner_id", Integer,
                              ForeignKey('person.company_id'),
                              nullable=False)
    number               = Column("number", String(100))
    first_name           = Column("firstname", String(50))
    last_name            = Column("name", String(50))
    is_account           = Column("is_account", Integer)
    is_person            = Column("is_person", Integer)
    is_private           = Column("is_private", Integer)
    is_read_only         = Column("is_readonly", Integer)
    is_customer          = Column("is_customer", Integer)
    is_extranet_account  = Column("is_extra_account", Integer)
    is_intranet_account  = Column("is_intra_account", Integer)
    version              = Column("object_version", Integer)
    URL                  = Column("url", String(255))
    login                = Column("login", String(50))
    password             = Column("password", String(50))
    salutation           = Column("salutation", String(50))
    degree               = Column("degree", String(50))
    birth_date           = Column("birthday", DateTime())
    gender               = Column("sex", String(10))
    middle_name          = Column("middlename", String(50))
    status               = Column("db_status", String(50))
    sensitivity          = Column("sensitivity", Integer)
    boss_name            = Column("boss_name", String(255))
    partner_name         = Column("partner_name", String(255))
    assistant_name       = Column("assistant_name", String(255))
    department           = Column("department", String(255))
    display_name         = Column("description", String(255))
    office               = Column("office", String(255))
    occupation           = Column("occupation", String(255))
    anniversary          = Column("anniversary", DateTime())
    FBURL                = Column("freebusy_url", String(255))
    file_as              = Column("fileas", String(255))
    im_address           = Column("im_address", String(255))
    associated_contacts  = Column("associated_contacts", String(255))
    associated_categories= Column("associated_categories", String(255))
    associated_company   = Column("associated_company", String(255))
    birth_place          = Column("birthplace", String(255))
    birth_name           = Column("birthname", String(255))
    family_status        = Column("family_status", String(255))
    citizenship          = Column("citizenship", String(255))
    grave_date           = Column("dayofdeath", DateTime())
    _keywords             = Column("keywords", String(255))
    # New
    source_url           = Column("source_url", String(255))
    ldap_url             = Column("dir_server", String(255))
    carddav_uid          = Column("carddav_uid", String(100))

    
    _info = relation( 'CompanyInfo', 
                      uselist = False,
                      backref = backref( 'company_info_contact' ),
                      primaryjoin = ( 'CompanyInfo.parent_id==Contact.object_id' ) )
    
    @property
    def comment(self):
        if self._info is None:
            self._info = CompanyInfo(text="")
        return self._info.text

    @comment.setter
    def comment(self, value):
        if self._info is None:
            self._info = CompanyInfo(text=value)
        else:
            self._info.text = value    

    def __init__(self):
        self.is_person = 1
        self.is_account = 0
        self.is_private = 0
        self.is_read_only = 0
        self.is_customer = 0
        self.is_extranet_account = 0
        self.is_intranet_account = 0
        self.gender = 'unknown'
        self.status = 'inserted'
        self._info = CompanyInfo()

    @property
    def keywords(self):
        if self._keywords:
            return self._keywords.split(' ')
        return []

    @keywords.setter
    def keywords(self, value):
        if isinstance(value, basestring):
            self._keywords = unicode(value)
        elif isinstance(value, list):
            tmp = [ unicode(x).strip() for x in value ]
            self._keywords = ' '.join(tmp)

    @property
    def ics_mimetype(self):
        return 'text/vcard'

    def get_company_value(self, name):
        cv = self.company_values.get( name, None )
        return cv

    def get_company_value_text(self, name, default=None):
        cv = self.company_values.get( name, None )
        if cv:
            if cv.string_value:
                return x.string_value
        return default

    def __cmp__(self, other):
        if (hasattr(other, 'object_id')):
            if (other.object_id > self.object_id):
                return -1
            elif (other.object_id < self.object_id):
                return 1
            return 0
        else:
            return 0

    def get_display_name(self):
        if self.file_as and len(self.file_as) > 3:
            return self.file_as
        elif self.last_name and self.first_name:
            return '{0}, {1}'.format(self.last_name, self.first_name)
        elif self.login:
            return self.login
        else:
            return 'OGo{0}'.format(self.object_id)

    def get_file_name(self):
        return self.carddav_uid if self.carddav_uid else '{0}.vcf'.format(self.object_id)

    def __repr__(self):
        return '<Contact objectId="{0}" version="{1}" displayName="{2}", login="{3}"/>'\
                .format(self.object_id, self.version, self.get_display_name(), self.login)
