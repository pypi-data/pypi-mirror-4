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
from datetime                    import datetime
from sqlalchemy                  import *
import sqlalchemy.orm            as orm
from base                        import Base, KVC


class Attachment(Base, KVC):
    __tablename__       = 'attachment'
    __entityName__      = 'Attachment'
    __internalName__    = 'Attachment' # Correct?
    uuid                = Column("attachment_id",
                                String(255),
                                primary_key=True)
    related_id          = Column("related_id", Integer,
                                 ForeignKey('person.company_id'),
                                 ForeignKey('enterprise.company_id'),
                                 ForeignKey('date_x.date_id'),
                                 ForeignKey('job.job_id'),
                                 ForeignKey('project.project_id'),
                                 ForeignKey('doc.document_id'),
                                 ForeignKey('route.route_id'),
                                 ForeignKey('process.process_id'),
                                 nullable=True)
    kind                = Column("kind", String(45), nullable=True)
    mimetype            = Column("mimetype", String(128), nullable=False)
    created             = Column("created", DateTime())
    size                = Column("size", Integer)
    expiration          = Column("expiration", Integer, nullable=True)
    context_id          = Column("context_id", Integer, nullable=False)
    webdav_uid          = Column('webdav_uid', String(128))
    checksum            = Column("checksum",  String(128))

    def __repr__(self):
        return '<Attachment UUID="{0}" relatedId={1} kind={2} mimetype="{3}" size={4} name={5} checksum="{6}">'.\
            format(self.uuid,
                   self.related_id if self.related_id else 'n/a',
                   '"{0}"'.format(self.kind) if self.kind else 'n/a',
                   self.mimetype,
                   self.size,
                   '"{0}"'.format(self.webdav_uid) if self.webdav_uid else 'n/a',
                   self.checksum)