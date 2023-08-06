### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
import os
from persistent import Persistent

# import Zope3 interfaces
from lovely.memcached.interfaces import IMemcachedClient
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.scheduler.interfaces import ISchedulerLocker, \
                                      IFileLockedScheduler, ISchedulerFileLockerInfo, \
                                      IMemcachedLockedScheduler, ISchedulerMemcachedLockerInfo

# import Zope3 packages
from zc.lockfile import LockFile, LockError
from zope.component import adapter, queryUtility
from zope.interface import implements, implementer
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.scheduler.jobstore import ShelveJobStore, MemcachedJobStore

from ztfy.scheduler import _


#
# Scheduler file locker
#

class SchedulerFileLocker(object):
    """Scheduler file locker"""

    implements(ISchedulerLocker)

    marker_interface = IFileLockedScheduler
    jobstore = None

    def getJobsStore(self, scheduler):
        info = ISchedulerFileLockerInfo(scheduler, None)
        if info is None:
            raise Exception(_("Scheduler is not configured to use file locking !"))
        jobstore = self.jobstore = ShelveJobStore(scheduler, os.path.join(info.locks_path, "scheduler_%d.jobs" % scheduler.internal_id))
        return jobstore

    def getLock(self, scheduler, task=None):
        info = ISchedulerFileLockerInfo(scheduler, None)
        if info is None:
            raise Exception(_("Scheduler is not configured to use file locking !"))
        if task is not None:
            lock_path = os.path.join(info.locks_path, "scheduler_%d.%d.lock" % (scheduler.internal_id, task.internal_id))
        else:
            lock_path = os.path.join(info.locks_path, "scheduler_%d.lock" % scheduler.internal_id)
        try:
            return LockFile(lock_path)
        except LockError:
            return None

    def releaseLock(self, lock):
        assert isinstance(lock, LockFile)
        lock.close()
        if os.path.exists(lock._path):
            os.unlink(lock._path)

SchedulerFileLocker = SchedulerFileLocker()


SCHEDULER_FILE_LOCKER_KEY = 'ztfy.scheduler.locker.file'

@adapter(IFileLockedScheduler)
@implementer(ISchedulerFileLockerInfo)
def SchedulerFileLockerFactory(context):
    """Scheduler file locker info adapter"""
    annotations = IAnnotations(context)
    locker = annotations.get(SCHEDULER_FILE_LOCKER_KEY)
    if locker is None:
        locker = annotations[SCHEDULER_FILE_LOCKER_KEY] = SchedulerFileLockerInfo()
    return locker


class SchedulerFileLockerInfo(Persistent):
    """Scheduler file locker info"""

    implements(ISchedulerFileLockerInfo)

    locks_path = FieldProperty(ISchedulerFileLockerInfo['locks_path'])


#
# Memcached file locker
#

class SchedulerMemcachedLocker(object):
    """Scheduler memcached locker"""

    implements(ISchedulerLocker)

    marker_interface = IMemcachedLockedScheduler
    jobstore = None

    def getJobsStore(self, scheduler):
        info = ISchedulerMemcachedLockerInfo(scheduler, None)
        if info is None:
            raise Exception(_("Scheduler is not configured to use memcached locking !"))
        jobstore = self.jobstore = MemcachedJobStore(scheduler)
        return jobstore

    def getLock(self, scheduler, task=None):
        info = ISchedulerMemcachedLockerInfo(scheduler, None)
        if info is None:
            raise Exception(_("Scheduler is not configured to use memcached locking !"))
        memcached = queryUtility(IMemcachedClient, info.memcached_client)
        if memcached is None:
            return None
        if task is not None:
            key = str("%s::%d.%d.lock" % (info.locks_namespace, scheduler.internal_id, task.internal_id))
        else:
            key = str("%s::%d.lock" % (info.locks_namespace, scheduler.internal_id))
        result = memcached.client.add(key, 'LOCKED')
        if not result:
            return None
        else:
            return (info, key)

    def releaseLock(self, lock):
        assert isinstance(lock, tuple)
        info, key = lock
        memcached = queryUtility(IMemcachedClient, info.memcached_client)
        if memcached is None:
            return None
        memcached.client.delete(key)


SchedulerMemcachedLocker = SchedulerMemcachedLocker()


SCHEDULER_MEMCACHED_LOCKER_KEY = 'ztfy.scheduler.lock.memcached'

@adapter(IMemcachedLockedScheduler)
@implementer(ISchedulerMemcachedLockerInfo)
def SchedulerMemcachedLockerFactory(context):
    """Scheduler memcached locker adapter"""
    annotations = IAnnotations(context)
    locker = annotations.get(SCHEDULER_MEMCACHED_LOCKER_KEY)
    if locker is None:
        locker = annotations[SCHEDULER_MEMCACHED_LOCKER_KEY] = SchedulerMemcachedLockerInfo()
    return locker


class SchedulerMemcachedLockerInfo(Persistent):
    """Scheduler memcached locker info"""

    implements(ISchedulerMemcachedLockerInfo)

    memcached_client = FieldProperty(ISchedulerMemcachedLockerInfo['memcached_client'])
    locks_namespace = FieldProperty(ISchedulerMemcachedLockerInfo['locks_namespace'])
