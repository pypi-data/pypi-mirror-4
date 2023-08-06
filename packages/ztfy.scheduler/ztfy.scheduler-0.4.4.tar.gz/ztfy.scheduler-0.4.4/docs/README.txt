======================
ztfy.scheduler package
======================

.. contents::

What is ztfy.scheduler ?
========================

ztfy.scheduler is a base package for those which need to build scheduled tasks which can run inside
a ZTK/ZopeApp based environment (ZEO is required !). These tasks can be scheduled:

 - on a cron-style base,
 - at a given date/time (like the "at" command)
 - or at a given interval.

Scheduling is done through the APScheduler (http://packages.python.org/APScheduler/) package and
so all these kinds of tasks can be scheduled with the same sets of settings. But tasks management
is made through a simple web interface and tasks running history is stored in the ZODB.

On application start, the scheduler is run in a dedicated ZeroMQ process, which is also used to
handle synchronization between tasks settings and scheduler jobs.

Tasks logs can be stored in the ZODB for a variable duration (based on a number of iterations).
These log reports can also be sent by mail, on each run or only when errors are detected.


How to use ztfy.scheduler ?
===========================

A set of ztfy.scheduler usages are given as doctests in ztfy/scheduler/doctests/README.txt
