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
from utcdatetime    import UTCDateTime

class Message(Base, KVC):
    """ An OpenGroupare message object """
    __tablename__       = 'message'
    __entityName__      = 'Message'
    __internalName__    = 'Message'
    uuid                = Column("uuid", String, primary_key=True)
    scope               = Column("scope", String)
    process_id          = Column("process_id", Integer)
    size                = Column("size", Integer)    
    status              = Column("db_status", String)
    label               = Column("label", String)
    mimetype            = Column("mimetype", String)
    version             = Column("object_version", Integer)
    created             = Column("creation_timestamp", UTCDateTime)
    modified            = Column("lastmodified", UTCDateTime)

    def __init__(self, process_id):
        self.process_id = process_id
        self.version = 0
        self.status = 'inserted'
        self.uuid = '{{{0}}}'.format(str(uuid4()))
        self.label = self.uuid
        self.mimetype = 'application/octet-stream'

    def get_payload(self):
        pass

    def store_payload(self, data):
        pass
        
    def __repr__(self):
        return '<Message GUID={0} version={1} processId="{2}"' \
                     ' label="{3}" size={4} mimeType="{5}">'.\
                format(self.uuid,
                       self.version,
                       self.process_id,
                       self.label,
                       self.size,
                       self.mimetype)        
