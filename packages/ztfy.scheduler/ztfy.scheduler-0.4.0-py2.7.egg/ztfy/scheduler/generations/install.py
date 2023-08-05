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

"""This ztfy.package generation modifies registered schedulers tasks
to remove scheduling modes marker interfaces which could be already included
due to a bug in a previous intermediate release.
"""

# import standard packages
import logging
logger = logging.getLogger('ztfy.scheduler')

# import Zope3 interfaces
from zope.component.interfaces import ISite
from zope.interface import providedBy, noLongerProvides

# import local interfaces
from ztfy.scheduler.interfaces import IScheduler, ISchedulerTaskSchedulingMarker

# import Zope3 packages
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtilitiesFor
from zope.site import hooks

# import local packages


def evolve(context):
    """Reset tasks provided interfaces"""
    logger.info("Updating ztfy.scheduler utilities...")
    root_folder = context.connection.root().get(ZopePublication.root_name, None)
    for site in root_folder.values():
        if ISite(site, None) is not None:
            hooks.setSite(site)
            for _name, scheduler in getUtilitiesFor(IScheduler):
                for task in scheduler.tasks:
                    for intf in providedBy(task):
                        if issubclass(intf, ISchedulerTaskSchedulingMarker):
                            noLongerProvides(task, intf)
