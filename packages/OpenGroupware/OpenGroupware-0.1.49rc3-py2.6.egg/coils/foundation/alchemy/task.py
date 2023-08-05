#
# Copyright (c) 2009, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime                  import datetime
from sqlalchemy                import *
from sqlalchemy.orm            import relation,backref, object_session
from utcdatetime               import UTCDateTime, UniversalTimeZone
from base                      import Base, KVC
from contact                   import Contact
from sqlalchemy.ext.associationproxy import association_proxy


class Task(Base, KVC):
    """ An OpenGroupare Task object """
    __tablename__       = 'job'
    __entityName__      = 'Task'
    __internalName__    = 'Job'
    object_id           = Column('job_id',
                                ForeignKey('log.object_id'),
                                ForeignKey('job.job_id'),
                                ForeignKey('object_acl.object_id'),
                                primary_key=True)
    version             = Column('object_version', Integer)
    parent_id           = Column('parent_job_id', Integer,
                                 ForeignKey('job.job_id'),
                                 nullable=True)
    project_id          = Column('project_id', Integer,
                                 ForeignKey('project.project_id'),
                                 nullable=True)
    creator_id          = Column('creator_id', Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=True)
    owner_id            = Column('owner_id', Integer,
                                 ForeignKey('person.company_id'),
                                 nullable=True)
    executor_id         = Column('executant_id', Integer,
                                 ForeignKey('person.company_id'),
                                 ForeignKey('team.company_id'),
                                 nullable=True)
    name                = Column('name', String(255))
    start               = Column('start_date', UTCDateTime)
    end                 = Column('end_date', UTCDateTime)
    completed           = Column('completion_date', UTCDateTime, nullable=True)
    notify              = Column('notify_x', Integer)
    state               = Column('job_status', String(255), nullable=False)
    status              = Column('db_status', String(50), nullable=False)
    category            = Column('category', String(255), nullable=True)
    kind                = Column('kind', String(50), nullable=True)
    keywords            = Column('keywords', String(255), nullable=True)
    sensitivity         = Column('sensitivity', Integer)
    priority            = Column('priority', Integer)
    comment             = Column('job_comment', String)
    complete            = Column('percent_complete', Integer)
    actual              = Column('actual_work', Integer)
    total               = Column('total_work', Integer)
    _modified            = Column('last_modified', Integer)
    accounting          = Column('accounting_info', String(255))
    travel              = Column('kilometers', String(255))
    associated_companies = Column('associated_companies', String(255))
    associated_contacts = Column('associated_contacts', String(255))
    timer               = Column('timer_date', UTCDateTime(), nullable=True)
    uid                 = Column('caldav_uid', String(100))
    href                = Column('source_url', String(255))


    @property
    def modified(self):
        if self._modified:
            return datetime.fromtimestamp(self._modified).replace(tzinfo=UniversalTimeZone())
        return None

    @modified.setter
    def modified(self, value):
        # TODO: Complete
        if value:
            if not value.tzinfo:
                value = value.replace(tzinfo=UniversalTimeZone())
            self._modified = int(value.strftime('%s'))
        else:
            self._modified = None

    def get_display_name(self):
        return self.name

    def get_file_name(self):
        return self.href if self.href else self.uid if self.uid else '{0}.ics'.format(self.object_id)

    @property
    def ics_mimetype(self):
        return 'text/vtodo'

    def __repr__(self):
        return '<Task objectId={0} version={1} name="{2}"' \
                    ' projectId={3} ownerId={4} creatorId={5}' \
                    ' start="{6}" end="{7}" status="{8}">'.\
                format(self.object_id,
                       self.version,
                       self.name,
                       self.project_id,
                       self.owner_id,
                       self.creator_id,
                       self.start.strftime('%Y-%m-%d'),
                       self.end.strftime('%Y-%m-%d'),
                       self.state)

    @property
    def graph_top(self):
        graph = { }
        top = self
        while top.parent:
            top = top.parent
        return top

    @property
    def graph(self):

        def level_down_(task):
            level_ = { }
            for child in task.children:
                level_[child.object_id] = level_down_(child)
            return level_

        top_ = self.graph_top
        return { top_.object_id: level_down_(top_) }


class TaskActionInfo(Base):
    __tablename__ = 'job_history_info'
    
    object_id     = Column('job_history_info_id', Integer,
                            Sequence('key_generator'),
                            primary_key=True)
    action_id     = Column('job_history_id', Integer, ForeignKey('job_history.job_history_id'))
    text          = Column('comment', String)
    status        = Column('db_status', String)

    def __repr__(self):
        return '<TaskActionInfo objectId={0} actionId={1}/>'.\
                format(self.object_id, self.action_id)
                
    _action = relation("TaskAction", 
                       uselist=False, 
                       backref=backref("_action", cascade="all, delete-orphan"),
                       primaryjoin=('TaskActionInfo.action_id==TaskAction.object_id'))       

def TaskActioInfoFactory():
    return TaskActionInfo()

class TaskAction(Base, KVC):
    __tablename__    = 'job_history'
    __entityName__   = 'taskNotation'
    __internalName__ = 'JobHistory'    
    
    object_id     = Column('job_history_id', Integer,
                           Sequence('key_generator'),
                           primary_key=True)
    task_id       = Column('job_id', Integer,
                           ForeignKey(Task.object_id))
    actor_id      = Column('actor_id', Integer,
                           ForeignKey(Contact.object_id),
                           nullable=False)
    action        = Column('action', String)
    action_date   = Column('action_date', UTCDateTime)
    task_status   = Column('job_status', String)

    def __init__(self):
        self.status = 'inserted'
        self._info = TaskActionInfo( )
        self._info.text = ''
        self._info.status = 'inserted'

    _info = relation( "TaskActionInfo", 
                      uselist=False,
                      backref=backref( 'job_history_info' ),
                      primaryjoin=( 'TaskActionInfo.action_id==TaskAction.object_id' ) )

    @property
    def comment(self):
        if self._info is None:
            self._info = TaskActionInfo( )
            self._info.comment = ''
            self._info.status = 'inserted'            
        return self._info.text

    @comment.setter
    def comment(self, value):
        if self._info is None:
            self._info = TaskActionInfo( )
            self._info.comment = value
            self._info.status = 'inserted'
        else:
            self._info.text = value 
