======================
ztfy.scheduler package
======================

.. contents::

What is ztfy.scheduler ?
========================

ztfy.scheduler is a base package for those which need to build scheduled tasks which can run inside
a Zope3/Bluebream environment (ZEO is required !). These tasks can be scheduled:

 - on a cron-style base,
 - at a given date/time (like the "at" command)
 - or at a given interval.

Scheduling is done through the APScheduler (http://packages.python.org/APScheduler/) package and
so all these kinds of tasks can be scheduled with the same sets of settings. But tasks management
is made through a simple web interface.

Locks management allows the scheduler to be integrated in a multi-process environment (via file locks)
or in a multi-hosts environment (via memcached locks), without the problem of tasks being run
simultaneously by several processes.

Tasks logs can be stored in the ZODB for a variable duration (based on a number of iterations).
These log reports can also be sent by mail, on each run or only when errors are detected.


How to use ztfy.scheduler ?
===========================

A set of ztfy.scheduler usages are given as doctests in ztfy/scheduler/doctests/README.txt


Known bugs
==========

 - Sometimes, deleting a task doesn't delete the matching job and the whole scheduler have to
   be restarted, generally via a whole server shutdown and restart.
