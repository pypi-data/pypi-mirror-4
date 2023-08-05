### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

# import Zope3 interfaces
from zope.component.interfaces import IObjectEvent
from zope.container.interfaces import IContainer

# import local interfaces
from ztfy.i18n.interfaces import II18nAttributesAware
from ztfy.security.interfaces import ILocalRoleManager

# import Zope3 packages
from zope.container.constraints import containers, contains
from zope.deprecation.deprecation import deprecated
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Text, Password, URI, Bool, Int, Datetime, Choice, List, Object

# import local packages
from ztfy.i18n.schema import I18nTextLine
from ztfy.security.schema import PrincipalList

from ztfy.scheduler import _


# Jobs run interfaces

class IBeforeJobRunEvent(IObjectEvent):
    """Interface for events notified before a job is run"""


class IAfterJobRunEvent(IObjectEvent):
    """Interface for events notified after a job run"""

    status = Attribute(_("Job execution status"))


# Scheduler task history interfaces

class ISchedulerTaskHistoryInfo(Interface):
    """Scheduler task history item"""

    date = Datetime(title=_("Execution date"),
                    required=True)

    status = Choice(title=_("Execution status"),
                    values=('OK', 'Warning', 'Error'))

    report = Text(title=_("Execution report"),
                  required=True)


# Scheduler task interfaces

class ISchedulerTaskInfo(Interface):
    """Base interface for scheduler tasks"""

    containers('ztfy.scheduler.interfaces.IScheduler')

    title = TextLine(title=_("Task name"),
                     description=_("Descriptive name given to this task"),
                     required=False)

    schedule_mode = Choice(title=_("Scheduling mode"),
                           description=_("Scheduling mode defines how task will be scheduled"),
                           vocabulary="ZTFY scheduling modes",
                           required=True)

    report_source = TextLine(title=_("Reports source"),
                             description=_("Mail address from which reports will be sent"),
                             required=False)

    report_target = TextLine(title=_("Reports target"),
                             description=_("Mail address to which execution reports will be sent"),
                             required=False)

    report_mailer = Choice(title=_("Reports mailer"),
                           description=_("Mail delivery utility used to send mails"),
                           required=False,
                           vocabulary='ZTFY mail deliveries')

    report_errors_only = Bool(title=_("Only report errors ?"),
                              description=_("It 'Yes', only error reports will be sent to given target"),
                              required=True,
                              default=False)

    history_length = Int(title=_("History length"),
                         description=_("Number of execution reports to keep in history; enter 0 to disable"),
                         required=True,
                         default=100)

    history = List(title=_("History"),
                   description=_("Task history"),
                   value_type=Object(schema=ISchedulerTaskHistoryInfo))

    runnable = Attribute(_("Is the task runnable ?"))

    internal_id = Attribute(_("Internal ID"))

    def getTrigger(self):
        """Get scheduler job trigger"""

    def getSchedulingInfo(self):
        """Get scheduling info"""

    def getNextRun(self):
        """Get next task execution time"""

    def run(self, db, root, site, report):
        """Launch job execution"""

    def storeReport(self, report, status):
        """Store execution report in task's history and send it by mail"""

    def sendReport(self, report):
        """Store execution report in task's history and send it by mail"""


class ISchedulerTaskWriter(Interface):
    """Scheduler task writer interface"""

    def reset(self):
        """Re-schedule job execution"""


class ISchedulerTask(ISchedulerTaskInfo, ISchedulerTaskWriter):
    """Scheduler task interface"""


class ISchedulerTaskSchedulingMode(Interface):
    """Scheduler task scheduling mode"""

    marker_interface = Attribute(_("Class name of scheduling mode marker interface"))

    schema = Attribute(_("Class name of scheduling mode info interface"))

    def getTrigger(self, task, scheduler):
        """Get trigger for the given task"""

    def schedule(self, task, scheduler):
        """Add given task to the scheduler"""


class ISchedulerTaskSchedulingInfo(Interface):
    """Base interface for task scheduling info"""

    active = Bool(title=_("Active task"),
                  description=_("You can disable a task by selecting 'No'"),
                  required=True,
                  default=False)

    max_runs = Int(title=_("Maximum number of iterations"),
                   description=_("Maximum number of times the job will be executed; keep empty for infinite execution.\n" +
                                 "WARNING: Counter is reset when server restarts or if task is re-scheduled."),
                   min=1,
                   required=False)

    start_date = Datetime(title=_("First execution date"),
                          description=_("Date from which scheduling should start"),
                          required=False)


class ISchedulerTaskSchedulingMarker(Interface):
    """Base interface for task scheduling mode markers"""


# Scheduler cron-style tasks interfaces

class ISchedulerCronTaskInfo(ISchedulerTaskSchedulingInfo):
    """Base interface for cron-style scheduled tasks"""

    year = TextLine(title=_("Years"),
                    description=_("Years for which to schedule the job"),
                    required=False,
                    default=u'*')

    month = TextLine(title=_("Months"),
                     description=_("Months (1-12) for which to schedule the job"),
                     required=False,
                     default=u'*')

    day = TextLine(title=_("Month days"),
                   description=_("Days (1-31) for which to schedule the job"),
                   required=False,
                   default=u'*')

    week = TextLine(title=_("Weeks"),
                    description=_("Year weeks (1-53) for which to schedule the job"),
                    required=False,
                    default=u'*')

    day_of_week = TextLine(title=_("Week days"),
                           description=_("Week days (0-6, with 0 as monday) for which to schedule the job"),
                           required=False,
                           default=u'*')

    hour = TextLine(title=_("Hours"),
                    description=_("Hours (0-23) for which to schedule the job"),
                    required=False,
                    default=u'*')

    minute = TextLine(title=_("Minutes"),
                      description=_("Minutes (0-59) for which to schedule the job"),
                      required=False,
                      default=u'*')

    second = TextLine(title=_("Seconds"),
                      description=_("Seconds (0-59) for which to schedule the job"),
                      required=False,
                      default=u'0')


class ISchedulerCronTask(ISchedulerTaskSchedulingMarker):
    """Target interface for cron-style scheduled tasks"""


# Scheduler dated tasks interfaces

class ISchedulerDateTaskInfo(ISchedulerTaskSchedulingInfo):
    """Base interface for date-based scheduled tasks"""


class ISchedulerDateTask(ISchedulerTaskSchedulingMarker):
    """Marker interface for date-based scheduled tasks"""


# Scheduler loop tasks interfaces

class ISchedulerLoopTaskInfo(ISchedulerTaskSchedulingInfo):
    """Base interface for interval-based scheduled tasks"""

    weeks = Int(title=_("Weeks interval"),
                description=_("Number of weeks between executions"),
                required=True,
                default=0)

    days = Int(title=_("Days interval"),
                description=_("Number of days between executions"),
                required=True,
                default=0)

    hours = Int(title=_("Hours interval"),
                description=_("Number of hours between executions"),
                required=True,
                default=0)

    minutes = Int(title=_("Minutes interval"),
                description=_("Number of minutes between executions"),
                required=True,
                default=1)

    seconds = Int(title=_("Seconds interval"),
                description=_("Number of seconds between executions"),
                required=True,
                default=0)


class ISchedulerLoopTask(ISchedulerTaskSchedulingMarker):
    """Marker interface for interval-based scheduled tasks"""


# ZODB packer task interface

class IZODBPackingTaskInfo(Interface):
    """ZODB packing task info"""

    zeo_connection = Choice(title=_("ZEO connection name"),
                            description=_("Name of ZEO connection utility pointing to packed database"),
                            required=True,
                            vocabulary="ZEO connections")

    pack_time = Int(title=_("Maximum transactions age"),
                    description=_("Transactions older than this age, in days, will be removed"),
                    required=True,
                    default=0)


class IZODBPackingTask(ISchedulerTask, IZODBPackingTaskInfo):
    """ZODB packing task interface"""


# Scheduler URL caller interface

class IURLCallerTaskInfo(Interface):
    """URL caller task info"""

    url = URI(title=_("Target URI"),
              description=_("Full URI of remote service"),
              required=True)

    username = TextLine(title=_("User name"),
                        description=_("Target login"),
                        required=False)

    password = Password(title=_("Password"),
                        description=_("Target password"),
                        required=False)

    proxy_server = TextLine(title=_("Proxy server"),
                            description=_("Proxy server name"),
                            required=False)

    proxy_port = Int(title=_("Proxy port"),
                     description=_("Proxy server port"),
                     required=False,
                     default=8080)

    remote_dns = Bool(title=_("Use remote DNS ?"),
                      description=_("If 'Yes', remote DNS queries will be done by proxy server"),
                      required=True,
                      default=True)

    proxy_username = TextLine(title=_("Proxy user name"),
                              required=False)

    proxy_password = Password(title=_("Proxy password"),
                              required=False)

    connection_timeout = Int(title=_("Connection timeout"),
                             description=_("Connection timeout, in seconds; keep empty to use system's default, which is also none by default"),
                             required=False,
                             default=30)


class IURLCallerTask(ISchedulerTask, IURLCallerTaskInfo):
    """URL caller interface"""


#
# Scheduler locks interfaces
#

#BBB: Deprecated
class IFileLockedScheduler(Interface):
    """Deprecated marker interface for schedulers using file locking"""
deprecated(IFileLockedScheduler, "Scheduler locking interfaces shoudn't be used anymore!")

#BBB: Deprecated
class IMemcachedLockedScheduler(Interface):
    """Deprecated marker interface for schedulers using memcached locking"""
deprecated(IMemcachedLockedScheduler, "Scheduler locking interfaces shoudn't be used anymore!")


#
# Scheduler interfaces
#

class ISchedulerHandler(Interface):
    """Scheduler management marker interface"""


class ISchedulerInfo(II18nAttributesAware):
    """Scheduler info interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Scheduler title"),
                         required=True)

    zmq_address = TextLine(title=_("Scheduler process address"),
                           description=_("""Address of scheduler listener, in the 'IPv4:port' format."""
                                         """Keep empty to disable it."""),
                           required=False,
                           default=u'127.0.0.1:5556')

    zeo_connection = Choice(title=_("ZEO connection name"),
                            description=_("Name of ZEO connection utility defining scheduler connection"),
                            required=True,
                            vocabulary="ZEO connections")

    internal_id = Attribute(_("Internal ID"))

    def getTask(self, task_id):
        """Get task matching given task ID"""

    def getJobs(self):
        """Get text output of running jobs"""

    def getNextRun(self, task):
        """Get next execution time of given task"""


class ISchedulerInnerInfo(Interface):
    """Scheduler internal info interface"""

    tasks = List(title=_("Scheduler tasks"),
                 description=_("List of tasks assigned to this scheduler"),
                 required=False)

    history = List(title=_("History"),
                   description=_("Task history"),
                   value_type=Object(schema=ISchedulerTaskHistoryInfo),
                   readonly=True)


class ISchedulerRoles(Interface):
    """Scheduler roles interface"""

    managers = PrincipalList(title=_("Scheduler managers"),
                             description=_("List of scheduler's managers, which can define scheduler settings"),
                             required=False)

    operators = PrincipalList(title=_("Scheduler operators"),
                              description=_("List of scheduler's operators, which can define tasks"),
                              required=False)


class IScheduler(ISchedulerInfo, ISchedulerInnerInfo, ISchedulerRoles, IContainer, ILocalRoleManager):
    """Tasks manager interface"""

    contains(ISchedulerTask)
