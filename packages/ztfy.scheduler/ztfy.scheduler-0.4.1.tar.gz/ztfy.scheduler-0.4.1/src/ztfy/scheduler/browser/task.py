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
from z3c.language.switch.interfaces import II18n

# import local interfaces
from ztfy.scheduler.browser.interfaces import ITaskPropertiesTarget, \
                                              ITaskActiveColumn
from ztfy.scheduler.interfaces import ISchedulerTask, ISchedulerTaskHistoryInfo, \
                                      ISchedulerCronTaskInfo, ISchedulerDateTaskInfo, \
                                      ISchedulerLoopTaskInfo, ISchedulerTaskInfo
from ztfy.skin.interfaces import IDefaultView, IContainedDefaultView
from ztfy.skin.layer import IZTFYBackLayer

# import Zope3 packages
from z3c.form import field
from z3c.table.column import Column, FormatterColumn, GetAttrColumn
from zope.component import adapts, queryMultiAdapter
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.traversing import namespace
from zope.traversing import api as traversing_api
from zope.traversing.browser import absoluteURL

# import local packages
from ztfy.jqueryui import jquery_datetime
from ztfy.skin.container import ContainerBaseView
from ztfy.skin.form import DialogAddForm, DialogDisplayForm, EditForm, DialogEditForm
from ztfy.skin.menu import MenuItem, JsMenuItem
from ztfy.skin.widget import FixedWidthTextAreaFieldWidget
from ztfy.utils.catalog import getIntIdUtility
from ztfy.utils.property import cached_property
from ztfy.utils.timezone import tztime
from ztfy.utils.traversing import getParent
from ztfy.utils.unicode import translateString

from ztfy.scheduler import _


class TaskDefaultViewAdapter(object):

    adapts(ISchedulerTask, IZTFYBackLayer, Interface)
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


class BaseTaskAddForm(DialogAddForm):

    @property
    def title(self):
        return II18n(self.context).queryAttribute('title', request=self.request)

    legend = _("Adding new scheduler task")

    fields = field.Fields(ISchedulerTaskInfo).omit('__parent__', '__name__', 'history')
    autocomplete = 'off'

    task_factory = None

    def create(self, data):
        task = self.task_factory()
        task.title = data.get('title')
        return task

    def add(self, task):
        name = translateString(task.title, forceLower=False, spaces='_')
        self.context[name] = task

    def getOutput(self, writer, parent):
        return writer.write({ 'output': 'RELOAD' })


class SchedulerTaskEditFormMenu(MenuItem):

    title = _("Connection settings")


class SchedulerTaskEditForm(EditForm):

    implements(ITaskPropertiesTarget)

    legend = _("Task properties")

    fields = field.Fields(ISchedulerTaskInfo).omit('__parent__', '__name__', 'history')
    autocomplete = 'off'

    def applyChanges(self, data):
        result = super(SchedulerTaskEditForm, self).applyChanges(data)
        if result:
            self.context.reset()
        return result


class TaskScheduleFormMenu(JsMenuItem):

    title = _(" :: Schedule...")

    def update(self):
        super(TaskScheduleFormMenu, self).update()
        jquery_datetime.need()


class BaseTaskScheduleForm(DialogEditForm):

    legend = _("Schedule selected task")

    def applyChanges(self, data):
        result = super(BaseTaskScheduleForm, self).applyChanges(data)
        self.context.reset()
        return result


class CronTaskScheduleForm(BaseTaskScheduleForm):

    fields = field.Fields(ISchedulerCronTaskInfo)


class DateTaskScheduleForm(BaseTaskScheduleForm):

    fields = field.Fields(ISchedulerDateTaskInfo)


class LoopTaskScheduleForm(BaseTaskScheduleForm):

    fields = field.Fields(ISchedulerLoopTaskInfo)


#
# Task tables columns
#

class TaskTitleColumn(Column):

    header = _("Title")
    weight = 10
    cssClasses = { 'td': 'title' }

    def renderCell(self, item):
        title = item.title
        if not title:
            title = traversing_api.getName(item)
        url = self.getURL(item)
        if url:
            title = '<a href="%s">%s</a>' % (url, title)
        return title

    def getURL(self, item):
        adapter = queryMultiAdapter((item, self.request, self.table), IContainedDefaultView)
        if adapter is None:
            adapter = queryMultiAdapter((item, self.request, self.table), IDefaultView)
        if adapter is not None:
            return adapter.getAbsoluteURL()


class TaskHistoryTitleColumn(TaskTitleColumn):

    def renderCell(self, item):
        task = getParent(item, ISchedulerTask)
        title = task.title
        if not title:
            title = traversing_api.getName(task)
        url = self.getURL(item)
        if url:
            title = '<a href="%s">%s</a>' % (url, title)
        return title

    def getURL(self, item):
        task = getParent(item, ISchedulerTask)
        return "javascript:$.ZTFY.dialog.open('%s/++history++%d/@@properties.html');" % \
            (absoluteURL(task, self.request),
             task.history.index(item))


class TaskActiveColumn(Column):

    implements(ITaskActiveColumn)

    header = _("Active ?")
    weight = 50

    cssClasses = { 'td': 'centered' }

    def renderCell(self, item):
        if item.runnable:
            return translate(_("Yes"), context=self.request)
        else:
            return translate(_("No"), context=self.request)


class TaskDeleteColumn(Column):

    header = u""
    weight = 80

    cssClasses = { 'td': 'actions' }

    def renderCell(self, item):
        klass = 'ui-workflow ui-icon ui-icon-trash'
        intids = getIntIdUtility()
        return '''<span title="%s" class="%s" onclick="$.ZTFY.container.remove(%s,this);"></span>''' % (translate(_("Delete task"), context=self.request),
                                                                                                        klass,
                                                                                                        intids.register(item))


class TaskHistoryDateColumn(FormatterColumn, GetAttrColumn):
    """Task history date column"""

    header = _("Execution date")
    weight = 20

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'date'

    def renderCell(self, item):
        formatter = self.getFormatter()
        value = self.getValue(item)
        if value:
            value = formatter.format(tztime(value))
        return '''<a href="javascript:$.ZTFY.dialog.open('%s/++history++%d/@@properties.html');">%s</a>''' % \
            (absoluteURL(self.context, self.request),
             self.context.history.index(item),
             value)


class TaskHistoryStatusColumn(GetAttrColumn):
    """Task history status column"""

    header = _("Status")
    weight = 30

    attrName = 'status'
    cssClasses = { 'td': 'centered' }


# Task history view

class TaskHistoryViewMenu(MenuItem):

    title = _("History")


class TaskHistoryView(ContainerBaseView):
    """Task history view"""

    legend = _("Task execution history")

    cssClasses = { 'table': 'history' }
    sortOn = None

    @property
    def values(self):
        return sorted(ISchedulerTask(self.context).history,
                      key=lambda x: x.date,
                      reverse=True)

    def renderRow(self, row, cssClass=None):
        item, _col, _span = row[0]
        status = item.status
        cssClass = cssClass and ('%s %s' % (cssClass, status)) or status
        return super(TaskHistoryView, self).renderRow(row, cssClass)


class TaskHistoryInfoNamespaceTraverser(namespace.view):
    """Task ++history++ namespace"""

    def traverse(self, name, ignored):
        index = int(name)
        return ISchedulerTask(self.context).history[index]


class TaskHistoryInfoDisplayDialog(DialogDisplayForm):
    """Task history info display dialog"""

    legend = _("Execution log")

    fields = field.Fields(ISchedulerTaskHistoryInfo)
    fields['report'].widgetFactory = FixedWidthTextAreaFieldWidget

    @property
    def title(self):
        return self.task.title

    @cached_property
    def task(self):
        return getParent(self.context, ISchedulerTask)
