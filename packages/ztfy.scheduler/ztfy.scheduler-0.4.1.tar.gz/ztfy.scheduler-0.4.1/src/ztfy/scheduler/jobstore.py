### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages
from apscheduler.jobstores.base import JobStore

# import Zope3 interfaces

# import local interfaces
from ztfy.utils.interfaces import IZEOConnection

# import Zope3 packages
from zope.component import getUtility, queryUtility
from zope.traversing.api import getParent, getPath

# import local packages


class ZODBJobsStore(JobStore):
    """ZODB jobs store"""

    def __new__(cls, scheduler_util, scheduler_process):
        zeo_connection_util = queryUtility(IZEOConnection, scheduler_util.zeo_connection)
        if zeo_connection_util is None:
            return None
        return JobStore.__new__(cls, scheduler_util, scheduler_process)

    def __init__(self, scheduler_util, scheduler_process):
        self.scheduler_util = scheduler_util
        self.scheduler_path = getPath(scheduler_util)
        self.scheduler_process = scheduler_process

    def load_jobs(self):
        jobs = []
        for task in self.scheduler_util.tasks:
            trigger = task.getTrigger()
            if trigger is not None:
                zeo_connection = getUtility(IZEOConnection,
                                            name=getParent(task).zeo_connection,
                                            context=task)
                job = self.scheduler_process.add_job(trigger, task, args=None,
                                                     kwargs={'zeo_settings': zeo_connection.getSettings()})
                job.id = task.internal_id
                jobs.append(job)
        self.jobs = jobs

    def add_job(self, job):
        if job not in self.jobs:
            self.jobs.append(job)

    def update_job(self, job):
        for index, my_job in enumerate(self.jobs):
            if my_job.id == job.id:
                self.jobs[index] = job

    def remove_job(self, job):
        if job in self.jobs:
            self.jobs.remove(job)

    def close(self):
        pass

    def __repr__(self):
        return '<%s (ZODB=%s)>' % (self.__class__.__name__, self.scheduler_util.zeo_connection)
