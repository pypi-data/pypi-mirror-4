#
# Copyright (c) 2010, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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
import logging
from datetime              import datetime
from collections           import deque

from apscheduler.scheduler import Scheduler
from apscheduler.triggers  import SimpleTrigger, IntervalTrigger, CronTrigger

from coils.foundation      import Parse_Value_To_UTCDateTime
from coils.core            import *
from job_store             import CoilsAlchemyJobStore


queue      = deque()

logger = logging.getLogger('coils.workflow.scheduler')

def enqueue_process(uuid, route_id, context_id, attachment_id, xattr_dict, priority=200):
    """
    This is the callback called when a job comes up for execution.  It adds it to the
    thread safe queue of processes to request-start.
    """
    global queue

    logging.info('Queued entry {0} [routeId#{1} contextId#{2} for execution'.format(uuid, route_id, context_id))
    queue.append( ( uuid, route_id, context_id, attachment_id, xattr_dict, priority ) )


class SchedulerService(Service):
    # TODO: Issue#63 - Deleted routes should be removed from schedule
    __service__ = 'coils.workflow.scheduler'
    __auto_dispatch__ = True
    __TimeOut__        = 60
    __DebugOn__       = None

    def __init__(self):
        self._ctx      = AdministrativeContext()
        Service.__init__(self)
        if (SchedulerService.__DebugOn__ is None):
            sd = ServerDefaultsManager()
            SchedulerService.__DebugOn__ = sd.bool_for_default('OIESchedulerDebugEnabled')

    @property
    def debug(self):
        return SchedulerService.__DebugOn__

    #
    # Run Queue Management
    #

    def service_run_queue(self):
        """
        Process the list of processes whose start should be requested.
        """
        if (self.debug):
            self.log.debug('Checking run_queue.')
        if (len(queue) > 0):
            self.log.debug('Have jobs in run queue.')
            run_queue = [ ]
            try:
                while True:
                    job = queue.pop()
                    run_queue.append(job)
            except IndexError:
                if (self.debug):
                    self.log.debug('Found {0} jobs in run queue'.format(len(run_queue)))
                for uuid, route_name, context_id, attachment_id, xattr_dict, priority in run_queue:
                    self.service_start_process(uuid, route_name, context_id, attachment_id, xattr_dict, priority)

    def service_start_process(self, uuid, route_id, context_id, attachment_id, xattr_dict, priority):
        """
        Request a process be started.  This reads the content of the
        specified attachement to the input message of the new process,
        and initializes that process for the specified context, then
        requests process start.  REMEMBER: it is up to the workflow
        manager when a process *actually* gets to run.

        :param uuid: The UUID name of the job. This is the UUID of the
            packet used to request the job be scheduled.
        :param route_id: The objectId of the route from which to
            construct the process.
        :param context_id: The objectId of the account whose security
            context and defaults will be used to execute the process.
        :param attachment_id: the UUID of the attachment that contains
            the input message content for the new process.  The MIME
            type of the attachment will be applied to the message.
        :param xattr_dict: a diction of XATTR properties to be created
            on the new process.
        :param priority:
        """
        ctx = AssumedContext(context_id, broker=self._broker)
        self.log.info('Attempting to start scheduled job {0}'.format(uuid))
        try:
            route = ctx.run_command('route::get', id=route_id)
            if route:
                # Assume no iput
                handle = None
                if attachment_id:
                    ''' An attachment id (a UUUD) was specified to provide the input
                        message for the new process.  Note that for a recurring schedule
                        the attachment content will be used repeatedly. '''
                    attachment = ctx.run_command('attachment::get', uuid=attachment_id)
                    if attachment:
                        handle = ctx.run_command('attachment::get-handle', attachment=attachment)
                    else:
                        ''' We were unable to find the specified attachment, perhaps
                            it has been deleted, or incorrectly specified when the
                            process was scheduled.  Send an administrative notice so
                            that the administrator can determine the cause of the problem. '''
                        message = "Scheduling indicates that a process should be created " \
                                  "but the attachment containting the input data could not " \
                                  "be found.\n" \
                                  " RouteId#{0}\n" \
                                  " ContextId#{1}\n" \
                                  " UUID:{2}\n" \
                                  " Attachment UUID: {3}\n".format( route_id,
                                                                    context_id,
                                                                    uuid,
                                                                    attachment_id )
                        self.send_administrative_notice(
                            category='workflow',
                            urgency=7,
                            subject='Unable to queue scheduled process; no attachment',
                            message=message)
                        raise CoilsException('Unable to marshall attachment for process input')
                if handle:
                    handle.seek(0, 2)
                    sizeof = handle.tell()
                    handle.seek(0, 0)
                    self.log.debug('Creating scheduled process with input from attachment; {0} bytes of "{1}" data.'.format(sizeof, attachment.mimetype))
                    process = ctx.run_command('process::new', values={ 'route_id': route.object_id,
                                                                       'priority': 200 },
                                                              handle = handle,
                                                              mimetype = attachment.mimetype )
                else:
                    self.log.debug('Creating scheduled process with no input data.')
                    process = ctx.run_command('process::new', values={ 'route_id': route.object_id,
                                                                       'priority': 200 },
                                                              data = '',
                                                              mimetype = 'text/plain' )

                self.log.info('objectId#{0} [Process] created'.format(process.object_id))

                # Move the values from xattr_dict to be XATTR properties on the shiny new process
                for key, value in xattr_dict.items():
                    key = 'xattr_{0}'.format(key.lower().replace(' ', ''))
                    if value is None:
                        value = 'YES'
                    else:
                        value = ActionCommand.scan_and_replace_labels( ctx, process, value, builtin_only=True )
                    ctx.property_manager.set_property(process,
                                                      'http://www.opengroupware.us/oie',
                                                      key, value)
                ctx.commit()
                # Good to go!
                ctx.run_command('process::start', process=process)
                ctx.commit()
                self.log.info('Scheduled job {0} is staged for execution.'.format(uuid))
            else:
                message = "Scheduling indicates that a process should be created " \
                          "but the specified route could not be found.\n" \
                          " RouteId#{0}\n" \
                          " ContextId#{1}\n" \
                          " UUID:{2}\n" \
                          " Length of Input Message: {3}\n".format(route_id,
                                                                   context_id,
                                                                   uuid,
                                                                   len(input_data))
                self.send_administrative_notice(subject="Route not available to create scheduled process",
                                                message=message,
                                                urgency=8,
                                                category='workflow')
                self.log.error('Unable to load routeID#{0} to create process'.format(route_id))
        except Exception, e:
            self.log.error('Failed to start scheduled process')
            self.log.exception(e)
            message = "An exception occurred in executing a scheduler entry.\n" \
                      " Exception: {0}\n" \
                      " RouteId#{1}\n" \
                      " ContextId#{2}\n" \
                      " UUID:{3}\n" \
                      " Attachment UUID: {4}\n".format(e,
                                                       route_id,
                                                       context_id,
                                                       uuid,
                                                       attachment_id)
            self.send_administrative_notice(
                category='workflow',
                urgency=9,
                subject='Exception creating workflow process from schedule',
                message=message)
        finally:
            ctx.close()

    def service_get_jobs(self, context_id, route_id):
        """
        Return the job objects available to the specified context,
        optionally limited by the specified route.

        :param context_id: The account objectId for the processes list.
        :param route_id: Optional route objectId used to filter the list,
            this route must be available to the specified context,
            otherwise an empty result is always returned.
        """
        results = [ ]
        ctx = AssumedContext(context_id)
        if route_id:
            route = ctx.run_command('route::get', id=route_id)
            if not route:
                return results
        else:
            route = None
        for job in self.scheduler.get_jobs():
            if len( job.args ) == 5:
                uuid, route_id, context_id, attachment_id, xattr_dict = job.args
                priority = 200
            else:
                uuid, route_id, context_id, attachment_id, xattr_dict, priority = job.args
            entry = False
            if (context_id in ctx.context_ids) or ctx.is_admin:
                if route:
                    if route.route_id == route_id:
                        results.append(job)
                else:
                    results.append(job)
        ctx.close()
        return results

    def service_cancel_job(self, context_id, job_id):
        ''' Find the job within the specified context with the provided
            id and remove it from the schedule.   This method will return
            True if a matching job was found and cancelled, or False if
            no corresponding job was found.

            :param context_id: The account objectId to provide the scope
                with which the job is searched; we don't want user's to
                be able to cancel each other's jobs.
            :param job_id: The UUID of the schedule entry that should
                be removed.
        '''

        jobs = self.service_get_jobs(context_id = context_id, route_id = None)
        for job in jobs:
            if job.name == job_id:
                self.scheduler.unschedule_job(job)
                break
        else:
            return False
        return True


    #
    # Plumbing
    #

    def prepare(self):
        """
        Service.prepare
        """
        Service.prepare(self)

        # Statup the APSchedular
        self.scheduler = Scheduler()
        self.scheduler.add_jobstore(
            CoilsAlchemyJobStore(
                engine=self._ctx.db_session().connection().engine,
            ),
            'backend'
        )
        self.scheduler.configure(misfire_grace_time=58)
        self.scheduler.start()

    def shutdown(self):
        """
            Shutdown the component; We override Service.shutdown so we
            can tell the APSchedular object/thread to shutdown.
        """
        self.schedular.shutdown(10)
        Service.shutdown(self)

    def work(self):
        """
        Run the process queue
        """
        self.service_run_queue()

    #
    # RPC methods
    #

    def do_list_jobs(self, parameter, packet):
        """
        RPC handler for the list_jobs method.  The request packet is e
        expected to contain a contextId value which corresponds to a
        valid security-context/account.  A routeId is optional to
        limited responses to scheduled instances of the indicated
        route.

        :param parameter: The parameter from the request packet.
        :param packet: The request packet
        """
        context_id = int(packet.data.get('contextId'))
        route_id   = int(packet.data.get('routeId', 0))

        result = [ ]
        for job in self.service_get_jobs(context_id, route_id):
            if len( job.args ) == 5:
                uuid, route_id, context_id, attachment_id, xattr_dict = job.args
                priority = 200
            else:
                uuid, route_id, context_id, attachment_id, xattr_dict, priority = job.args

            # Create a route name
            # TODO: perhaps we should do this under the specified context?
            if route_id:
                route = self._ctx.run_command( 'route::get', id=route_id)
                if route:
                    route_name = route.name
                else:
                    route_name = 'Unknown'
            else:
                route_name = 'Adhoc'

            # Compute remaining job runs
            max_runs = job.max_runs
            if max_runs:
                remaining_runs = max_runs - job.runs
            else:
                remaining_runs = -1

            entry = { 'UUID': uuid,
                      'priority': priority,
                      'routeId': route_id,
                      'routeName': route_name,
                      'contextId': context_id,
                      'attachmentUUID': attachment_id,
                      'iterationsPerformed': job.runs,
                      'iterationsRemaining': remaining_runs,
                      'nextIteration': job.compute_next_run_time( datetime.now( ) ),
                      'xattrDict': xattr_dict, }

            if isinstance(job.trigger, SimpleTrigger):
                entry.update( { 'type': 'simple',
                                'date': job.trigger.run_date } )

            elif isinstance(job.trigger, IntervalTrigger):
                entry.update( { 'type':      'interval',
                                'interval':  job.trigger.interval.seconds,
                                'start':     job.trigger.start_date } )

            elif isinstance(job.trigger, CronTrigger):
                entry['type'] = 'cron'
                for field in job.trigger.fields:
                    # HACK: rename the day_of_week back to dayOfWeek
                    if field.name == 'day_of_week':
                        name = 'dayOfWeek'
                    else:
                        name = field.name
                    value = ','.join((str(e) for e in field.expressions))
                    entry[name] = value
            result.append(entry)
        self.send(Packet.Reply(packet, { u'status':   200,
                                         u'schedule': result } ) )

    def do_schedule_job(self, parameter, packet):
        """
        RPC handler for the schedule_job method.  This packet is
        expected to contain at least the following values -
          * routeId
          * contextId
          * triggerType
        Optional values are -
          * attachmentUUID
          * xattrDict
        For triggerType == "simple" a "date" value is required.
        For triggerType == "interval" the following values are procesed -
          * weeks, days, hours, minutes, seconds
          * start
        For triggerType == "cron" the following values are procesed -
          * year, month, day, weekday, hour, minute

        :param parameter: The parameter from the request packet.
        :param packet: The request packet
        """

        try:
            route_id      = int( packet.data.get( 'routeId' ) )
            context_id    = int( packet.data.get( 'contextId' ) )
            priority      = int( packet.data.get( 'priority', 200 ) )
            attachment_id = packet.data.get( 'attachmentUUID', None )
            xattr_dict    = dict( packet.data.get( 'xattrDict', { } ) )
            trigger       = str( packet.data.get( 'triggerType') )

            repeats       = packet.data.get( 'repeat', None )
            if repeats:
                repeats = int( repeats )

            if trigger == 'simple':
                # Date job
                if (self.debug):
                    self.log.debug('Scheduling date job')
                # HACK: APSchedular is timezone naive, so we need to de-localize our values
                fire_date = Parse_Value_To_UTCDateTime( time_value = packet.data.get( 'date' ) )
                fire_date = fire_date.replace( tzinfo=None )
                self.log.debug( 'Localized value "{0}" to "{1}"'.format( packet.data.get( 'date' ), fire_date ) )
                self.scheduler.add_date_job( func     = enqueue_process,
                                             date     = fire_date,
                                             max_runs = repeats,
                                             name     = packet.uuid,
                                             jobstore = 'backend',
                                             args = ( packet.uuid,
                                                      route_id,
                                                      context_id,
                                                      attachment_id,
                                                      xattr_dict,
                                                      priority ) )
            elif trigger == 'interval':
                # Interval
                if (self.debug):
                    self.log.debug('Scheduling interval job')
                # HACK: APSchedular is timezone naive, so we need to de-localize our values
                start_date = Parse_Value_To_UTCDateTime( time_value = packet.data.get( 'start', None ),
                                                         default    = datetime.utcnow( ) )
                start_date = start_date.replace( tzinfo=None )
                self.log.debug( 'Localized value "{0}" to "{1}"'.format( packet.data.get( 'start', None ), start_date ) )
                self.scheduler.add_interval_job( func       = enqueue_process,
                                                 name       = packet.uuid,
                                                 max_runs   = repeats,
                                                 weeks      = int(packet.data.get('weeks', 0)),
                                                 days       = int(packet.data.get('days', 0)),
                                                 hours      = int(packet.data.get('hours', 0)),
                                                 minutes    = int(packet.data.get('minutes', 0)),
                                                 seconds    = int(packet.data.get('seconds', 0)),
                                                 start_date = start_date,
                                                 jobstore   = 'backend',
                                                 args = ( packet.uuid,
                                                          route_id,
                                                          context_id,
                                                          attachment_id,
                                                          xattr_dict,
                                                          priority ) )
            elif trigger == 'cron':
                # Crontab style
                if (self.debug):
                    self.log.debug('Scheduling chronological job')
                self.scheduler.add_cron_job( func        = enqueue_process,
                                             name        = packet.uuid,
                                             max_runs    = repeats,
                                             year        = str(packet.data.get('year', '*')),
                                             month       = str(packet.data.get('month', '*')),
                                             day         = str(packet.data.get('day', '*')),
                                             day_of_week = str(packet.data.get('dayOfWeek', '*')),
                                             hour        = str(packet.data.get('hour', '*')),
                                             minute      = str(packet.data.get('minute', '*')),
                                             jobstore    = 'backend',
                                             args = ( packet.uuid,
                                                      route_id,
                                                      context_id,
                                                      attachment_id,
                                                      xattr_dict,
                                                      priority ) )
        except Exception, e:
            self.log.exception(e)
            self.send(Packet.Reply(packet, { u'status': 500,
                                             u'text': unicode(e),
                                             u'UUID': None}))
        else:
            self.send(Packet.Reply(packet, { u'status': 200,
                                             u'text': 'Process scheduled OK',
                                             u'UUID': packet.uuid}))
        self._ctx.db_session().commit()

    def do_unschedule_job(self, parameter, packet):
        """
        RPC handler for the schedule_job method.  This packet is
        expected to contain at least the following values -
          * routeId
          * contextId
          * triggerType
        Optional values are -
          * attachmentUUID
          * xattrDict
        For triggerType == "simple" a "date" value is required.
        For triggerType == "interval" the following values are procesed -
          * weeks, days, hours, minutes, seconds
          * start
        For triggerType == "cron" the following values are procesed -
          * year, month, day, weekday, hour, minute

        :param parameter: The parameter from the request packet.
        :param packet: The request packet
        """

        job_id = packet.data.get('UUID')
        if not job_id:
            self.send(Packet.Reply(packet, { u'status': 500,
                                             u'text':   u'No UUID specified in unschedule_job message' } ) )
            return
        context_id = packet.data.get('contextId', 8999)
        if self.service_cancel_job(job_id = job_id, context_id = context_id):
            self._ctx.db_session().commit()
            self.send(Packet.Reply(packet, { u'status': 200,
                                             u'UUID':   job_id,
                                             u'text':  'Job cancelled.' } ) )
        else:
            self.send(Packet.Reply(packet, { u'status': 404,
                                             u'UUID':   job_id,
                                             u'text':   u'No such job as "{0}"'.format(job_id) } ) )
