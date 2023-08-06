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
# THE SOFTWARE.
#
from datetime       import datetime
from uuid           import uuid4
from sqlalchemy     import *
from base           import Base, KVC

class AuthenticationToken(Base, KVC):
    """ An OpenGroupware Authentication Token object """
    __tablename__       = 'login_token'
    __entityName__      = 'AuthenticationToken'
    __internalName__    = 'AuthenticationToken'
    token                 = Column("token", String(4096),
                                primary_key=True)
    account_id            = Column("account_id", Integer,
                                ForeignKey('person.company_id'),
                                nullable=False)
    created               = Column("creation_date", DateTime())
    touched               = Column("touch_date", DateTime())
    expiration            = Column("expiration_date", DateTime())
    timeout               = Column("timeout", Integer)

    def __init__(self):
        self.token      = '{0}-{1}-{2}'.format(uuid4(), uuid4(),  uuid4())
        self.created    = datetime.now()
        self.touched    = datetime.now()
        self.timeout    = 120
        self.expiration = None
