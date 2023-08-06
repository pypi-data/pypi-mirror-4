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

# import Zope3 interfaces

# import local interfaces
from ztfy.scheduler.browser.interfaces import ITaskAddFormMenuTarget
from ztfy.scheduler.interfaces import IScheduler, ISchedulerInfo, ISchedulerRoles
from ztfy.skin.interfaces import IDefaultView, IPropertiesMenuTarget
from ztfy.skin.layer import IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.template.template import getLayoutTemplate
from zope.component import adapts
from zope.interface import implements, Interface
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.jqueryui import jquery_multiselect
from ztfy.security.browser import ztfy_security
from ztfy.security.browser.roles import RolesEditForm
from ztfy.skin.container import ContainerBaseView
from ztfy.skin.form import EditForm, DialogEditForm, DisplayForm
from ztfy.skin.menu import JsMenuItem, MenuItem

from ztfy.scheduler import _


class SchedulerDefaultViewAdapter(object):
    """Scheduler default view adapter"""

    adapts(IScheduler, IZTFYBackLayer, Interface)
    implements(IDefaultView)

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view

    @property
    def viewname(self):
        return '@@properties.html'

    def getAbsoluteURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request), self.viewname)


class SchedulerEditForm(EditForm):
    """Scheduler properties edit form"""

    implements(IPropertiesMenuTarget)

    fields = field.Fields(ISchedulerInfo)

    legend = _("Edit scheduler properties")
    help = _("""If the scheduler is already registered, you should unregister it to stop it, """
             """change it's properties and register it again.""")

    successMessage = _("""Data successfully updated.\n"""
                       """WARNING: you should restart application process if scheduler """
                       """address has been changed without being unregistered!""")


class SchedulerRolesMenuItem(JsMenuItem):
    """Scheduler roles menu item"""

    title = _(":: Roles...")

    def update(self):
        super(SchedulerRolesMenuItem, self).update()
        ztfy_security.need()
        jquery_multiselect.need()


class SchedulerRolesEditForm(DialogEditForm, RolesEditForm):
    """Scheduler roles edit form"""

    interfaces = (ISchedulerRoles,)
    layout = getLayoutTemplate()
    parent_interface = IScheduler


class SchedulerHistoryViewMenu(MenuItem):
    """Scheduler history view menu"""

    title = _("Tasks run history")


class SchedulerHistoryView(ContainerBaseView):
    """Scheduler history view"""

    legend = _("Scheduler tasks execution history")

    cssClasses = { 'table': 'history' }
    sortOn = None

    @property
    def values(self):
        return sorted(IScheduler(self.context).history,
                      key=lambda x: x.date,
                      reverse=True)

    def renderRow(self, row, cssClass=None):
        item, _col, _span = row[0]
        status = item.status
        cssClass = cssClass and ('%s %s' % (cssClass, status)) or status
        return super(SchedulerHistoryView, self).renderRow(row, cssClass)


class SchedulerTasksViewMenu(MenuItem):
    """Scheduler tasks view menu"""

    title = _("Tasks")


class SchedulerTasksView(ContainerBaseView):
    """Scheduler tasks view"""

    implements(ITaskAddFormMenuTarget)

    legend = _("Scheduler's tasks")

    @property
    def values(self):
        return IScheduler(self.context).tasks


class SchedulerJobsViewMenu(MenuItem):
    """Scheduler jobs view menu"""

    title = _("Jobs")


class SchedulerJobsView(DisplayForm):
    """Scheduler jobs view"""

    title = _("Scheduler jobs")
    legend = _("List of currently scheduled jobs")

    @property
    def jobs(self):
        return removeSecurityProxy(self.context.getJobs())
