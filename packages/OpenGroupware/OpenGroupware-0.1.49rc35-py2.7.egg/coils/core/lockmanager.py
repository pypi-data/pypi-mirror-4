#
# Copyright (c) 2011, 2012, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
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
import uuid, json
from datetime         import datetime
from coils.foundation import Lock
from sqlalchemy       import *
from exception        import AccessForbiddenException

class LockManager(object):
    __slots__ = ( '_ctx' )

    def __init__(self, ctx):
        self._ctx = ctx

    def _now(self):
        return int( datetime.utcnow( ).strftime( '%s' ) )

    def _check_context_id(self, context_id):
        '''
        Check that the context specified is legal for the operational context.
        :param context_id: context id the code is attempting to use
        '''

        #SECURITY: prevent code from specifying a context_id it isn't allowed to use
        if self._ctx.is_admin and context_id:
            pass
        elif context_id and context_id in self._ctx.context_ids:
            pass
        elif not context_id:
            context_id = self._ctx.account_id
        else:
            raise AccessForbiddenException( 'Only an administrative context can specify an arbitrary lock context' )

        return context_id

    def locks_on(self, entity, all_locks=False, delete=False, write=True, run=False, exclusive=True):
        """
        Returns all the locks on the specified entity with the described application(s).

        :param entity: entity to check for locks
        :param all_locks: if set locks will be returned regardless of application.
        :param delete: limit locks to those with a delete application
        :param write: limit locks to those with a write application
        :param run: limit locks to those with a run application
        :param exclusive: limit locks to exclusive locks
        """
        db = self._ctx.db_session( )
        t = self._now( )
        clause = and_ ( Lock.object_id == entity.object_id,
                        Lock.granted <= t,
                        Lock.expires >= t )
        if not all_locks:
            if exclusive: clause.append( Lock.exclusive == 'Y' )
            if run: clause.append( Lock.operations.like('%r%') )
            if write: clause.append( Lock.operations.like('%w%') )
            if delete: clause.append( Lock.operations.like('%d%') )
        query = db.query( Lock ).filter( clause )
        return query.all( )

    def can_upgrade(self, mylock, alllocks, delete, write, run, exclusive, context_id=None):
        '''
        Determine if the specified lock can be upgraded to the requested mode(s)
        :param mylock:
        :param alllocks:
        :param delete:
        :param write:
        :param run:
        :param exclusive:
        :param context_id:
        '''

        context_id = self._check_context_id( context_id )

        # The mode of an exclusive lock can always be changed
        if mylock.is_exclusive:
            return True

        # If the mode has not changed, the typical case, then change is OK!
        if ( delete == mylock.delete and write == mylock.write and
             run == mylock.run and exclusive == mylock.is_exclusive ):
            return True

        # Filter out my lock from the list of all locks
        locks = [x for x in alllocks if x != mylock ]
        # Return fail as soon as we hit an overlap with another lock
        for otherlock in locks:
            if otherlock.is_exclusive and other.owner_id != context_id:
                # An exclusive lock is held by another user, request denied
                return False
            if otherlock.run and mylock.run:
                # A run lock already exists on an entity
                return False
            if otherlock.write and mylock.write:
                # A write lock already exists on the entity
                return False
            if otherlock.delete and mylock.delete:
                # A delete lock already exists on an entity
                return False
        return True

    def lock(self, entity, duration, data, delete=False, write=True, run=False, exclusive=True, context_id=None):
        """
        Apply, upgrade, or resh a lock on the entity for a given application. By default if no
        application is specified the lock will be write+exclusive.

        :param entity:
        :param duration:
        :param data:
        :param delete:
        :param write:
        :param run:
        :param exclusive:
        """

        context_id = self._check_context_id( context_id )

        db = self._ctx.db_session( )
        my_lock = None
        locks = self.locks_on( entity, all_locks=True  )
        for lock in locks:
            if ( ( lock.owner_id != context_id ) and
                 ( lock.exclusive ) ):
                # Someone else has an exclusive lock on this object
                return False, lock
            elif ( lock.owner_id == context_id ):
                my_lock = lock
        if my_lock:
            if self.can_upgrade( my_lock, locks, delete=delete, write=write, run=run, exclusive=exclusive ):
                self.refresh( token=my_lock.token, duration=duration, data=data, context_id=context_id )
                my_lock.update_mode(delete=delete, write=write, run=run, exclusive=exclusive)
                return True, my_lock
            else:
                return False, None
        else:

            my_lock = Lock( owner_id=context_id,
                            object_id=entity.object_id,
                            duration=duration,
                            data=data,
                            delete=delete,
                            write=write,
                            run=run,
                            exclusive=exclusive )
            self._ctx.db_session( ).add( my_lock )
        return True, my_lock

    def refresh(self, token, duration, data=None, context_id=None):
        """
        Refresh the specified lock for an addition period of time. The application
        of the lock is not changed. If the lock referred to is not found or has
        expired a None is returned; if the lock is refreshed the Lock entity is
        returned.

        :param token:
        :param duration:
        :param data:
        """

        context_id = self._check_context_id( context_id )

        t = self._now()
        db = self._ctx.db_session()
        query = db.query(Lock).filter(and_(Lock.token == token,
                                           Lock.owner_id  == context_id,
                                           Lock.granted <= t,
                                           Lock.expires >= t ) )
        data = query.all()
        if data:
            # Take the first lock
            my_lock = data[ 0 ]
            my_lock.expires = self._now() + duration
            return my_lock
        return None


    def unlock(self, entity, token=None, context_id = None):
        """
        Remove all the locks on a specified entity or the specified
        lock [via token] on the specified entity.  If token is specified it
        must be a lock on the references entity.

        :param entity: The entity on which the lock or locks should be removed.
        :param token: The token of an individual lock to be removed.
        """

        context_id = self._check_context_id( context_id )

        db = self._ctx.db_session()
        if token:
            query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                               Lock.owner_id  == context_id,
                                               Lock.token     == token ) )
        else:

            query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                               Lock.owner_id  == context_id ) )
        locks = query.all( )
        if locks:
            for lock in locks:
                self._ctx.db_session( ).delete( lock )
            return True
        return False

    def get_lock(self, token):
        """
        Retrieve the lock entity with the specified token. If the token does not
        reference a current lock None will be returned.

        :param token: The lock token (string)
        """

        t = self._now()
        db = self._ctx.db_session()
        query = db.query(Lock).filter( and_( Lock.token == token,
                                             Lock.granted <= t,
                                             Lock.expires >= t ) )
        data = query.all()
        if data:
            return data[ 0 ]
        return None

    def is_locked(self, entity, delete=False, write=False, run=False, exclusive=False):
        """
        Return True of False indicating if any locks of the specified application
        are applied to the entity.

        :param entity:
        :param delete:
        :param write:
        :param run:
        :param exclusive:
        """
        locks = self.locks_on(entity, delete=delete, write=write, run=run, exclusive=exclusive)
        if locks:
            return True
        return False

    def have_lock(self, entity, run=False, delete=False, write=False, exclusive=False, context_id=None):
        """
        Return True or False indicating if the current context has a lock of the specified
        application.

        :param entity:
        :param run:
        :param delete:
        :param write:
        :param exclusive:
        """

        context_id = self._check_context_id( context_id )

        locks = self.locks_on( entity, delete=delete,
                                       write=write,
                                       run=run,
                                       exclusive=exclusive,
                                       context_id=context_id )
        return bool( [ lock for lock in locks if lock.owner_id == context_id ] )


class AdministrativeLockManager(LockManager):
    '''
    An AdminitrativeContext returns this as the "lockmanager" instead of the plain
    non-Administrative LockManager; this subclass adds some additional methods that
    allow locks to be manipulated regardless of ownership.
    '''

    def administratively_refresh_lock(self, token, duration=3600):
        '''
        Refresh the specified, extending its life-span.
        :param token: The lock token
        :param duration: The duration to extend the lock life-span from now.
        '''
        lock = self._ctx.db_session( ).query( Lock ).filter( Lock.token == token )
        if lock:
            lock.expires = self._now() + duration
            return True
        return False

    def administratively_release_lock(self, token):
        '''
        Delete the specified lock
        :param token: the token of the lock to be deleted.
        '''
        if self._ctx.db_session( ).query( Lock ).filter( Lock.token == token ).\
            delete( synchronize_session='evaluate' ):
            return True
        return False
