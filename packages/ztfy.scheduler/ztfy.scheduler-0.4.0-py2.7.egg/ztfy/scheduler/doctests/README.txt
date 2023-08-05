======================
ZTFY.scheduler package
======================

WARNING
-------

!!! Automatic execution of these doctests are actually broken !!!
!!! Doctests should be upgraded to conform to last package revision... :-( !!!


Introduction
------------

This package includes a set of utilities and base classes which can be used to define
background tasks which can be run using several kinds of settings matching different kinds
of tasks:

 - cron-style tasks are defined as well known Unix cron tasks ; you can define year(s),
   month(s), day(s), week(s), day(s) of week(s), hour(s), minute(s) and/or second(s) at
   which the task have to be launched

 - date-based tasks are tasks which are scheduled to run only once at a specific date and
   time

 - repeatable tasks are tasks which are scheduled to run repeatedly according to an interval
   time given in weeks, days, hours, minutes and seconds ; the first date and time execution
   as week as the number of executions can also be defined.

These kinds of tasks can be used to handle operations like database packing, automatic 
transitions in a workflow management context, background file conversion or indexing (see
'ztfy.blog.video' package for example) or many others.

WARNING: all these kinds of tasks are actually defined to be run as ZEO clients, each running
in a separate thread; in a context where you have several ZEO clients to serve a single application,
you should generally take care to run each task only from a single ZEO client. Dedicating a single
ZEO client to handle all background tasks is generally a good choice.

WARNING: actually, the first default action of a running task is to traverse the ZEO database to
it's own path to check if it's OK to be run ; so each task have to be created with the same path
on it's "source" database as well as on it's "target" database. If you need or want a different
behavior, you will have to override the "_run" method of BaseTask class.

WARNING: transactions are not actually handled by default by base tasks classes; if your task
needs to handle transactions, you have to take care of them in the "run" method".
To get the transaction manager, DON'T USE the default one that you get by importing transaction
but use the ITransactionManager adapter provided by this package (and copied from *zc.twist* package).

WARNING: a task can handle it's own settings or data which can be modified during task execution.
In this use case, and as the ZEO database connection is kept open between jobs executions, you **MUST**
commit or abort your transaction at the beginning of your job execution to be sure to use fresh data.


Definitions
-----------

A task is the definition and settings of a task to schedule; a job is the concrete
instantiation of a given task actually scheduled at a given time.


Scheduler handler
-----------------

The scheduler handler is the first utility to declare ; without it, no scheduling task
will be run !

The goal of the scheduling handler is to manage schedulers and running jobs.

    >>> import zope.component
    >>> import zope.interface
    >>> from ztfy.scheduler.interfaces import ISchedulerHandler
    >>> from ztfy.scheduler.manager import SchedulerHandler

    >>> handler = SchedulerHandler()
    >>> zope.component.provideUtility(handler, ISchedulerHandler)

    >>> from zope.location.traversing import LocationPhysicallyLocatable
    >>> zope.component.provideAdapter(LocationPhysicallyLocatable)

Scheduler handler registration can be done easily in ZCML via a simple "<handler />" directive,
which is defined in "http://namespaces.ztfy.org/scheduler" namespace.


Scheduler utility
-----------------

Once the scheduling handler is registered, we can create a concrete scheduler ; it's a 
persistent container class defined to store tasks.

    >>> from zope.intid.interfaces import IIntIds
    >>> class DummyIntId(object):
    ...     zope.interface.implements(IIntIds)
    ...     MARKER = '__dummy_int_id__'
    ...     def __init__(self):
    ...         self.counter = 0
    ...         self.data = {}
    ...     def register(self, obj):
    ...         intid = getattr(obj, self.MARKER, None)
    ...         if intid is None:
    ...             setattr(obj, self.MARKER, self.counter)
    ...             self.data[self.counter] = obj
    ...             intid = self.counter
    ...             self.counter += 1
    ...         return intid
    ...     def queryId(self, obj):
    ...         return self.register(obj)
    ...     def getObject(self, intid):
    ...         return self.data[intid]
    ...     def __iter__(self):
    ...         return iter(self.data)
    >>> intid = DummyIntId()
    >>> zope.component.provideUtility(intid, IIntIds)

    >>> from ztfy.scheduler.interfaces import IScheduler
    >>> from ztfy.scheduler.manager import Scheduler
    >>> scheduler = Scheduler()
    >>> scheduler.zmq_address = u'127.0.0.1:6666'
    >>> zope.component.provideUtility(scheduler, IScheduler)

    >>> from ztfy.scheduler.events import handleRegisteredSchedulerUtility
    >>> handleRegisteredSchedulerUtility(scheduler, None)

Now we can start the scheduler ; this is done automatically as soon as the database is opened
for each registered scheduler, or when a new scheduler utility is registered.

    >>> scheduler.getJobs()
    []


Creating a sample task
----------------------

We will just create a sample task as a sample ; it's a repeatable task which just print "Hello !"
every second...

For a "normal" task, you just have to override the "run" method, which receives tree arguments :

 - the database the job is connected to

 - the root of the database

 - the site manager of the given task


    >>> from ztfy.scheduler.task import LoopTask
    >>> class HelloTask(LoopTask):
    ...     def connect(self):
    ...         pass
    ...     def get_root(self, db=None):
    ...         pass
    ...     def _run(self):
    ...         if self.runnable:
    ...             self.run(None, None, None)
    ...     def run(self, report):
    ...         print "Hello !"

    >>> task = HelloTask()
    >>> task.repeat = 2
    >>> task.seconds = 1
    >>> scheduler['HelloTask'] = task
    >>> task.schedule()
    >>> scheduler.get_jobs()
    []

Jobs are only created for active tasks.
Task must be activated before it can be executed:

    >>> task.active = True
    >>> task.schedule()
    >>> scheduler.getJobs()
    [<Job (name=HelloTask, trigger=<IntervalTrigger (interval=datetime.timedelta(0, 1), start_date=datetime.datetime(...))>)>]
    >>> import time
    >>> time.sleep(3)
    Hello !
    Hello !
    Hello !

Task scheduling is done manually here but in the context of a normal site management, it's done
automatically by the scheduler as soon as the task is added to it.


Tests cleanup
-------------

Stop scheduler and wait for everything to shut down...

    >>> scheduler.stop()
    >>> time.sleep(1)
