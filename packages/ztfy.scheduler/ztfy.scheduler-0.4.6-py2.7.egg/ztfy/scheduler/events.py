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
import atexit
import logging
logger = logging.getLogger('ztfy.scheduler')

import time
import transaction
import zmq

# import Zope3 interfaces
from transaction.interfaces import ITransactionManager
from zope.catalog.interfaces import ICatalog
from zope.component.interfaces import ISite, IRegistered, IUnregistered, IComponentRegistry
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.processlifetime import IDatabaseOpenedWithRoot

# import local interfaces
from ztfy.scheduler.interfaces import ISchedulerHandler, IScheduler, ISchedulerTask
from ztfy.security.interfaces import ILocalRoleIndexer
from ztfy.utils.interfaces import INewSiteManagerEvent

# import Zope3 packages
from zc.catalog.catalogindex import SetIndex
from zope.app.publication.zopepublication import ZopePublication
from zope.catalog.catalog import Catalog
from zope.component import hooks, getUtilitiesFor, queryUtility, adapter
from zope.intid import IntIds
from zope.location.location import locate
from zope.traversing import api as traversing_api

# import local packages
from ztfy.scheduler.process import SchedulerProcess, SchedulerMessageHandler
from ztfy.utils.site import locateAndRegister
from ztfy.zmq.process import processExitFunc


_schedulers = {}


def updateDatabaseIfNeeded(context):
    """Check for missing utilities at application startup"""
    try:
        sm = context.getSiteManager()
    except:
        return
    default = sm['default']
    # Check for required IIntIds utility
    intids = queryUtility(IIntIds)
    if intids is None:
        intids = default.get('IntIds')
        if intids is None:
            intids = IntIds()
            locate(intids, default)
            IComponentRegistry(sm).registerUtility(intids, IIntIds, '')
            default['IntIds'] = intids
    # Check for security catalog and indexes
    catalog = default.get('SecurityCatalog')
    if catalog is None:
        catalog = Catalog()
        locateAndRegister(catalog, default, 'SecurityCatalog', intids)
        IComponentRegistry(sm).registerUtility(catalog, ICatalog, 'SecurityCatalog')
    if catalog is not None:
        if 'ztfy.SchedulerManager' not in catalog:
            index = SetIndex('ztfy.SchedulerManager', ILocalRoleIndexer, False)
            locateAndRegister(index, catalog, 'ztfy.SchedulerManager', intids)
        if 'ztfy.SchedulerOperator' not in catalog:
            index = SetIndex('ztfy.SchedulerOperator', ILocalRoleIndexer, False)
            locateAndRegister(index, catalog, 'ztfy.SchedulerOperator', intids)


@adapter(IDatabaseOpenedWithRoot)
def handleOpenedDatabase(event):
    """Launch scheduler process"""
    handler = queryUtility(ISchedulerHandler)
    if handler is None:
        return
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, {})
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            manager = ITransactionManager(site)
            for attempt in manager.attempts():
                with attempt as t:
                    updateDatabaseIfNeeded(site)
                if t.status == 'Committed':
                    break
            for _name, utility in getUtilitiesFor(IScheduler):
                if utility.zmq_address:
                    try:
                        try:
                            path = traversing_api.getPath(utility)
                        except:
                            # Can't get utility path ?
                            # probably an unregistered deleted utility, go on...
                            continue
                        else:
                            if _schedulers.get(path) is None:
                                process = SchedulerProcess(utility, SchedulerMessageHandler)
                                process.start()
                                time.sleep(2)
                                if process.is_alive():
                                    _schedulers[path] = process
                                    atexit.register(processExitFunc, process=process)
                                logger.info("Starting ZMQ process %s listening on %s with PID %d for handler %s" %
                                            (process.name, utility.zmq_address,
                                             process.pid, str(process.handler)))
                    except zmq.ZMQError, e:
                        logger.warning("Can't start scheduler process: " + e.message)


@adapter(INewSiteManagerEvent)
def handleNewSiteManager(event):
    updateDatabaseIfNeeded(event.object)


@adapter(IScheduler, IRegistered)
def handleRegisteredSchedulerUtility(utility, event):
    if utility.zmq_address:
        path = traversing_api.getPath(utility)
        if _schedulers.get(path) is None:
            process = SchedulerProcess(utility, SchedulerMessageHandler)
            process.start()
            time.sleep(2)
            if process.is_alive():
                _schedulers[path] = process
                atexit.register(processExitFunc, process=process)
            logger.info("Starting ZMQ process %s listening on %s with PID %d for handler %s" %
                        (process.name, utility.zmq_address,
                         process.pid, str(process.handler)))


@adapter(IScheduler, IUnregistered)
def handleUnregisteredSchedulerUtility(utility, event):
    try:
        path = traversing_api.getPath(utility)
    except:
        # Can't get utility path ?
        # Probably an already deleted utility, go on as we can't do anything...
        # System will have to be restarted to restart scheduler process.
        return
    else:
        process = _schedulers.get(path)
        if process is not None:
            process.terminate()
            process.join()
            logger.info("Stopped unregistered scheduler process %s with PID %d" % (process.name, process.pid))
            del _schedulers[path]


def _deleteSchedulerHook(*args, **kw):
    """After commit hook for scheduler deletion"""
    path = kw.get('scheduler_path')
    if path is not None:
        process = _schedulers.get(path)
        if process is not None:
            process.terminate()
            process.join()
            logger.info("Stopped deleted scheduler process %s with PID %d" % (process.name, process.pid))
            del _schedulers[path]


@adapter(IScheduler, IObjectRemovedEvent)
def handleDeletedScheduler(utility, event):
    transaction.get().addAfterCommitHook(_deleteSchedulerHook, kws={ 'scheduler_path': traversing_api.getPath(utility) })


@adapter(ISchedulerTask, IObjectRemovedEvent)
def handleDeletedTask(task, event):
    """Reset deleted tasks..."""
    task.reset()
