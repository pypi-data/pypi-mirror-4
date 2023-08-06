#
# Copyright (c) 2009, 2012
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
from sqlalchemy     import *
from base           import Base, KVC
from company        import CompanyInfo
from sqlalchemy.orm import relation,backref
from sqlalchemy.ext.associationproxy import association_proxy



class Enterprise(Base, KVC):
    """ An OpenGroupware Enterprise object """
    __tablename__        = 'enterprise'
    __entityName__       = 'Enterprise'
    __internalName__     = 'Enterprise'
    object_id            = Column("company_id", Integer,
                                  ForeignKey('object_acl.object_id'),
                                  ForeignKey('log.object_id'),
                                  primary_key=True)
    version               = Column("object_version", Integer)
    name                  = Column("description", String(45))
    bank                  = Column("bank", String(100))
    bank_code             = Column("bank_code", String(45))
    email                 = Column("email", String(100))
    is_enterprise         = Column("is_enterprise", Integer)
    is_private            = Column("is_private", Integer)
    is_read_only          = Column("is_readonly", Integer)
    is_customer           = Column("is_customer", Integer)
    sensitivity           = Column("sensitivity", Integer)    
    associated_contacts   = Column("associated_contacts", String(255))
    associated_categories = Column("associated_categories", String(255))
    associated_company    = Column("associated_company", String(255))
    im_address            = Column("im_address", String(255))
    keywords              = Column("keywords", String(255))
    URL                   = Column("url", String(255))
    owner_id              = Column("owner_id", Integer)
    file_as               = Column("fileas", String(255))
    status                = Column("db_status", String(50))
    number                = Column("number", String(50))
    login                 = Column("login", String(100))
    carddav_uid          = Column("carddav_uid", String(100))

    _info = relation("CompanyInfo", 
                    uselist=False,
                    backref=backref('company_info_enterprise'),
                    primaryjoin=('CompanyInfo.parent_id==Enterprise.object_id'))    
                    
    ''' comment = association_proxy('_info', 'text') '''
    
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
        self.is_enterprise = 1
        self.is_private = 0
        self.is_read_only = 0
        self.is_customer = 0
        self.status = 'inserted'
        self._info = CompanyInfo()

    def get_display_name(self):
        return self.name

    def get_file_name(self):
        return self.carddav_uid if self.carddav_uid else '{0}.vcf'.format(self.object_id)

