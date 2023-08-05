#
# Copyright (c) 2009, 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from uuid           import uuid4
from sqlalchemy     import *
from base           import Base, KVC
from utcdatetime    import UTCDateTime


"""
CREATE TABLE process (
  process_id        INTEGER NOT NULL,
  guid              CHARACTER VARYING(128),
  route_id          INTEGER NOT NULL,
  owner_id          INTEGER NOT NULL,
  object_version    INTEGER DEFAULT 0,
  input_message     CHARACTER VARYING(128) NOT NULL,
  db_status         CHARACTER(15),
  output_message    CHARACTER VARYING(128),
  started           TIMESTAMP(6) WITH TIME ZONE,
  completed         TIMESTAMP(6) WITH TIME ZONE,
  parked            TIMESTAMP(6) WITH TIME ZONE,
  state             CHARACTER(1) DEFAULT ''I'::bpchar',
  priority          INTEGER DEFAULT 0,
  task_id           INTEGER,
    PRIMARY KEY (process_id)
  )
"""


class Process(Base, KVC):
    """ An OpenGroupare process object """
    __tablename__       = 'process'
    __entityName__      = 'Process'
    __internalName__    = 'Process'
    object_id           = Column("process_id", Integer,
                                ForeignKey('log.object_id'),
                                ForeignKey('object_acl.object_id'),    
                                primary_key=True)
    uuid                = Column('guid', String)
    route_id            = Column('route_id', Integer,
                                 ForeignKey('route.route_id'))
    priority            = Column('priority', Integer)
    task_id             = Column('task_id', Integer)
    status              = Column('db_status', String)
    version             = Column('object_version', Integer)
    owner_id            = Column('owner_id', Integer,
                                ForeignKey('person.company_id'),
                                nullable=False)
    state               = Column('state', String(1), quote=True)
    input_message       = Column('input_message', String)
    output_message      = Column('output_message', String)
    started             = Column('started', UTCDateTime)
    parked              = Column('parked', UTCDateTime)
    created             = Column('created', UTCDateTime)
    modified            = Column('lastmodified', UTCDateTime)
    completed           = Column('completed', UTCDateTime)

    def __init__(self):
        self.status = 'inserted'
        self.state  = 'I'
        self.priority = 0
        self.uuid = '{{{0}}}'.format(str(uuid4()))

    def set_markup(self, text):
        setattr(self, '_markup', text)

    def get_markup(self):
        if (hasattr(self, '_markup')):
            return getattr(self, '_markup')
        return None   
        
    def __repr__(self):
        return '<Process objectId={0} version={1} routeId="{2}"' \
                     ' ownerId={3}>'.\
                format(self.object_id,
                       self.version,
                       self.route_id,
                       self.owner_id)
