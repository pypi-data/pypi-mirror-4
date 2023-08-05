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
from sqlalchemy     import *
from base           import Base, KVC
from utcdatetime    import UTCDateTime

class Route(Base, KVC):
    """ An OpenGroupare route object """
    __tablename__       = 'route'
    __entityName__      = 'Route'
    __internalName__    = 'Route'
    object_id           = Column("route_id",
                                ForeignKey('log.object_id'),
                                ForeignKey('object_acl.object_id'),
                                primary_key=True)
    name                = Column("name", String(50))
    status              = Column("db_status", String)
    comment             = Column("comment", Text)
    created             = Column('created', UTCDateTime)
    modified            = Column('lastmodified', UTCDateTime)
    version             = Column("object_version", Integer)
    owner_id            = Column("owner_id", Integer,
                                ForeignKey('person.company_id'),
                                nullable=False)

    def __init__(self):
        self.status = 'inserted'

    def set_markup(self, text):
        self._markup = text

    def get_markup(self):
        if (hasattr(self, '_markup')):
            return self._markup
        return None

    def get_display_name(self):
        return self.name

    def __repr__(self):
        return '<Route objectId={0} version={1} name="{2}"' \
                     ' owner={3}>'.\
                format(self.object_id,
                       self.version,
                       self.name,
                       self.owner_id)
