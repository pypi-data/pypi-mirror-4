#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import ORMEntity, UniversalTimeZone, UTCDateTime
from sqlalchemy  import types, Column, String, Integer, func, BOOLEAN
from sqlalchemy.dialects.postgresql import ARRAY
from edition import INDEXER_EDITION

class TextSearchVector(types.UserDefinedType):
    def get_col_spec(self):
        return 'plainto_tsvector'

class SearchVector(ORMEntity):
    __tablename__ = 'vista_vector'
    object_id     = Column('object_id',  Integer, primary_key=True)
    entity        = Column('entity',     String)
    version       = Column('version',    Integer)
    edition       = Column('edition',    Integer)
    archived      = Column('archived',   BOOLEAN, default=False)
    event_date    = Column('event_date', UTCDateTime)
    keywords      = Column('keywords',   ARRAY(String))
    vector        = Column('vector',     TextSearchVector, nullable=False)

    def __init__(self, object_id, entity, version, edition):
        self.object_id = object_id
        self.entity = entity.lower()
        self.version = version
        self.edition = INDEXER_EDITION
