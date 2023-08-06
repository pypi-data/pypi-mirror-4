#
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
#
import pickle
import logging

from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore
from apscheduler.job import Job
from sqlalchemy import *

logger = logging.getLogger(__name__)

class CoilsAlchemyJobStore(SQLAlchemyJobStore):
    def __init__(self, url=None, 
                       engine=None, 
                       tablename='process_schedule',
                       metadata=None, 
                       pickle_protocol=pickle.HIGHEST_PROTOCOL):
        self.jobs = []
        self.pickle_protocol = pickle_protocol

        if engine:
            self.engine = engine
        elif url:
            self.engine = create_engine(url)
        else:
            raise ValueError('Need either "engine" or "url" defined')

        self.jobs_t = Table(tablename, metadata or MetaData(),
            Column('id', Integer,
                   Sequence(tablename + '_id_seq', optional=True),
                   primary_key=True),
            Column('trigger', PickleType(pickle_protocol, mutable=False),
                   nullable=False),
            Column('func_ref', String(1024), nullable=False),
            Column('args', PickleType(pickle_protocol, mutable=False),
                   nullable=False),
            Column('kwargs', PickleType(pickle_protocol, mutable=False),
                   nullable=False),
            Column('name', Unicode(1024)),
            Column('misfire_grace_time', Integer, nullable=False),
            Column('coalesce', Boolean, nullable=False),
            Column('max_runs', Integer),
            Column('max_instances', Integer),
            Column('next_run_time', DateTime, nullable=False),
            Column('runs', BigInteger))

        self.jobs_t.create(self.engine, True)

    def add_job(self, job):
        job_dict = job.__getstate__()
        result = self.engine.execute(self.jobs_t.insert().values(**job_dict))
        job.id = result.inserted_primary_key[0]
        self.jobs.append(job)
        #print('added job {0}'.format(job))

    def remove_job(self, job):
        delete = self.jobs_t.delete().where(self.jobs_t.c.id == job.id)
        self.engine.execute(delete)
        self.jobs.remove(job)
        #print('removed job {0}'.format(job))

    def load_jobs(self):
        jobs = []
        for row in self.engine.execute(select([self.jobs_t])):
            try:
                job = Job.__new__(Job)
                job_dict = dict(row.items())
                job.__setstate__(job_dict)
                jobs.append(job)
            except Exception:
                job_name = job_dict.get('name', '(unknown)')
                logger.exception('Unable to restore job "%s"', job_name)
        self.jobs = jobs
        #print('loaded {0} jobs'.format(len(self.jobs)))

    def update_job(self, job):
        job_dict = job.__getstate__()
        update = self.jobs_t.update().where(self.jobs_t.c.id == job.id).\
            values(next_run_time=job_dict['next_run_time'],
                   runs=job_dict['runs'])
        self.engine.execute(update)
        #print('updated job {0}'.format(job))

    def close(self):
        self.engine.dispose()

    def __repr__(self):
        return '<%s (url=%s)>' % (self.__class__.__name__, self.engine.url)
