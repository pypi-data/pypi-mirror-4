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
import zmq

# import Zope3 interfaces
from zope.intid.interfaces import IIntIds

# import local interfaces
from ztfy.scheduler.interfaces import IScheduler, ISchedulerHandler

# import Zope3 packages
from zope.component import queryUtility
from zope.container.folder import Folder
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.site.site import SiteManagerContainer

# import local packages
from ztfy.i18n.property import I18nTextProperty
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.property import cached_property


class SchedulerHandler(object):
    """Scheduler handler utility"""

    implements(ISchedulerHandler)


class Scheduler(Folder, SiteManagerContainer):
    """Scheduler persistent class"""

    implements(IScheduler)

    title = I18nTextProperty(IScheduler['title'])
    zmq_address = FieldProperty(IScheduler['zmq_address'])
    zeo_connection = FieldProperty(IScheduler['zeo_connection'])

    managers = RolePrincipalsProperty(IScheduler['managers'], role='ztfy.SchedulerManager')
    operators = RolePrincipalsProperty(IScheduler['operators'], role='ztfy.SchedulerOperator')

    @property
    def tasks(self):
        return list(self.values())

    @property
    def history(self):
        result = []
        [ result.extend(task.history) for task in self.tasks ]
        return result

    @cached_property
    def internal_id(self):
        intids = queryUtility(IIntIds, context=self)
        if intids is not None:
            return intids.register(self)

    def getTask(self, task_id, context=None):
        intids = queryUtility(IIntIds, context=context)
        return intids.queryObject(task_id)

    def _getSocket(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://' + self.zmq_address)
        return socket

    def getJobs(self):
        socket = self._getSocket()
        socket.send_json(['get_jobs', {}])
        return socket.recv_json()
