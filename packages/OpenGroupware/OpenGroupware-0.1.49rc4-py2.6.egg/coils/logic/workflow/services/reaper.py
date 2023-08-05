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
from datetime         import date
from sqlalchemy.orm   import aliased
from sqlalchemy       import and_, or_
from coils.core       import AdministrativeContext, Process, Route, \
                             ObjectProperty, Service, ServerDefaultsManager, \
                             Packet

class ReaperService(Service):
    __service__ = 'coils.workflow.reaper'
    __auto_dispatch__ = True
    __is_worker__     = True
    __TimeOut__       = 60

    def __init__(self):
        Service.__init__(self)

    def prepare(self):
        Service.prepare(self)
        self.counter = 0 # HACK, we should do this better
        ReaperService.__ExpireDays__ = ServerDefaultsManager().integer_for_default('OIEDefaultProcessExpirationDays', 15)
        self._ctx = AdministrativeContext({}, broker=self._broker)

    def work(self):
        if self.counter > 10:
            result = self._reap()
            if result:
                self.log.debug('Reaper reaped {0} expired processes.'.format(len(result)))
            self.counter = 0
        self.counter += 1

    def _reap(self, pid=None):
        
        reaped_pids = [ ]
        
        db = self._ctx.db_session()

        op1 = aliased(ObjectProperty)
        op2 = aliased(ObjectProperty)
        op3 = aliased(ObjectProperty)

        q = db.query( Process, op1, op2, op3 ).\
               join( Route, Route.object_id == Process.route_id ).\
               outerjoin( op1, and_( op1.parent_id == Route.object_id, 
                                     op1.namespace=='http://www.opengroupware.us/oie',
                                     op1.name=='expireDays' ), ).\
               outerjoin( op2, and_( op2.parent_id == Route.object_id, 
                                     op2.namespace=='http://www.opengroupware.us/oie',
                                     op2.name=='preserveAfterCompletion' ), ).\
               outerjoin( op3, and_( op3.parent_id == Route.object_id, 
                                     op3.namespace=='http://www.opengroupware.us/oie',
                                     op3.name=='archiveAfterExpiration' ), ).\
               filter( and_( Process.state.in_( [ 'C', 'F', 'Z' ] ), 
                             Process.status != 'archived' ) )
       
        # This is a request to reap a specific process
        if pid:
            q = q.filter(Process.object_id == pid)
        
        result = q.all()
        for process, expire_days, preserve_after, archive_after in result:
            if self._reap_process(process, expire_days, preserve_after, archive_after):
                reaped_pids.append(process.object_id)
        self._ctx.commit()
        return reaped_pids

    def _reap_process(self, process, expire_days, preserve_after, archive_after):

        if process.completed:
            
            today = date.today().toordinal()
            
            completed = process.completed.toordinal()
            
            expiration = completed + ReaperService.__ExpireDays__
            if expire_days:
                if expire_days._integer_value:
                    # A negative expire days value should result in infinite preservation
                    if expire_days._integer_value < 0:
                        expiration = -1
                    else:
                        expiration = completed + expire_days._integer_value
                else:
                    # TODO: Send administrative notice about invalid expireDays value
                    expiration = completed + ( ReaperService.__ExpireDays__ * 3 )
              

            if not process.state == 'C':
                preserve_after = True
            else:
                # Completed processes default to deletion (no preservation), but this
                # is toggled by setting {http://www.opengroupware.us/oie}preserveAfterCompletion
                # to a string value which compares to YES;  as a safety precaution if we find
                # this property but it isn't a string value [not even sure how that can happen]
                # we fall back to preserving the process.  It will expire eventually anyway.                
                if preserve_after:
                    preserve_after = preserve_after.get_value()
                    if isinstance(preserve_after, basestring):
                        if preserve_after.upper() == 'YES':
                            preserve_after = True
                        else:
                            preserve_after = False
                    else:
                        preserve_after = True
                else:
                    preserve_after = False

            if archive_after:
                archive_after = archive_after.get_value()
                if isinstance(archive_after, basestring):
                    if archive_after.upper() == 'YES':
                        archive_after = True
                    else:
                        archive_after = False
                else:
                    # TODO: Send Administrative Notice
                    archive_after == True
            else:
                archive_after = False
                
            if ( ( expiration > 0 ) and (expiration < today ) ) or ( not preserve_after ):
                if not archive_after:
                    self._ctx.run_command('process::delete', object=process)
                    self.log.info('Reaper deleted process objectId#{0}'.format(process.object_id))
                    return True
                else:
                    self._ctx.run_command('process::archive', pid=process.object_id)
                    self.log.info('Reaper archived process objectId#{0}.'.format(process.object_id))
                    return True

        return False

    def do_deleteprocess(self, parameter, packet):
        # NOTE: This method is obsolete and no longer does anything at all
        self.send(Packet.Reply(packet, {'STATUS': 201, 'MESSAGE': 'OK'}))
        return

