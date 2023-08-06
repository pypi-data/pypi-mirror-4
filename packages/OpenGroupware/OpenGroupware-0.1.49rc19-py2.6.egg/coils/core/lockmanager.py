#
# Copyright (c) 2011, 2012
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

class LockManager(object):
    __slots__ = ('_ctx')

    def __init__(self, ctx):
        self._ctx = ctx

    def _now(self):
        return int(datetime.utcnow().strftime('%s'))

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

    def can_upgrade(self, mylock, alllocks, delete, write, run, exclusive):
        
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
            if otherlock.is_exclusive and other.owner_id != self._ctx.account_id:
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

    def lock(self, entity, duration, data, delete=False, write=True, run=False, exclusive=True):
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
        db = self._ctx.db_session( )
        my_lock = None
        locks = self.locks_on( entity, all_locks=True  )
        for lock in locks:
            if ( ( lock.owner_id != self._ctx.account_id ) and
                 ( lock.exclusive ) ):
                # Someone else has an exclusive lock on this object
                return False, lock
            elif ( lock.owner_id == self._ctx.account_id ):
                my_lock = lock
        if my_lock:
            if self.can_upgrade( my_lock, locks, delete=delete, write=write, run=run, exclusive=exclusive ):
                self.refresh( token=my_lock.token, duration=duration, data=data )
                my_lock.update_mode(delete=delete, write=write, run=run, exclusive=exclusive)
                return True, my_lock
            else:
                return False, None
        else:

            my_lock = Lock( owner_id=self._ctx.account_id, 
                            object_id=entity.object_id, 
                            duration=duration, 
                            data=data,
                            delete=delete, 
                            write=write, 
                            run=run,
                            exclusive=exclusive )
            self._ctx.db_session( ).add( my_lock )        
        return True, my_lock

    def refresh(self, token, duration, data=None):
        """
        Refresh the specified lock for an addition period of time. The application
        of the lock is not changed. If the lock referred to is not found or has 
        expired a None is returned; if the lock is refreshed the Lock entity is
        returned.
        
        :param token:
        :param duration:
        :param data:
        """
        t = self._now()
        db = self._ctx.db_session()
        query = db.query(Lock).filter(and_(Lock.token == token,
                                           Lock.owner_id  == self._ctx.account_id,
                                           Lock.granted <= t,
                                           Lock.expires >= t ) )
        data = query.all()
        if data:
            # Take the first lock
            my_lock = data[ 0 ]
            my_lock.expires = self._now() + duration
            return my_lock
        return None


    def unlock(self, entity, token=None):
        """
        Remove all the locks on a specified entity or the specified
        lock [via token] on the specified entity.  If token is specified it
        must be a lock on the references entity.
        
        :param entity: The entity on which the lock or locks should be removed.
        :param token: The token of an individual lock to be removed.
        """
        db = self._ctx.db_session()
        if token:
            query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                               Lock.owner_id  == self._ctx.account_id,
                                               Lock.token     == token ) )
        else:
            
            query = db.query(Lock).filter(and_(Lock.object_id == entity.object_id,
                                               Lock.owner_id  == self._ctx.account_id))
        locks = query.all()
        if locks:
            for lock in locks:
                self._ctx.db_session().delete(lock)
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

    def have_lock(self, entity, run=False, delete=False, write=False, exclusive=False):
        """
        Return True or False indicating if the current context has a lock of the specified 
        application.
        
        :param entity:
        :param run:
        :param delete:
        :param write:
        :param exclusive:
        """
        locks = self.locks_on( entity, delete=delete, write=write, run=run, exclusive=exclusive )
        return bool( [ lock for lock in locks if lock.owner_id == self._ctx.account_id ] )

