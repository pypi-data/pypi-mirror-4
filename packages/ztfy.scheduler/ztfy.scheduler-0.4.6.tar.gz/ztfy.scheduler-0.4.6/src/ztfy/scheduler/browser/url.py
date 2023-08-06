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


# import standard packages

# import Zope3 interfaces
from z3c.form import field

# import local interfaces
from ztfy.scheduler.interfaces import IURLCallerTaskInfo

# import Zope3 packages

# import local packages
from ztfy.scheduler.browser.task import BaseTaskAddForm
from ztfy.scheduler.url import URLCallerTask
from ztfy.skin.form import DialogEditForm
from ztfy.skin.menu import DialogMenuItem

from ztfy.scheduler import _


class URLCallerTaskAddForm(BaseTaskAddForm):
    """URL caller add form"""

    task_factory = URLCallerTask


class URLCallerTaskAddFormMenu(DialogMenuItem):
    """URL caller task add form menu"""

    title = _(" :: Add URL caller...")
    target = URLCallerTaskAddForm


class URLCallerTaskEditForm(DialogEditForm):
    """URL caller task edit form"""

    fields = field.Fields(IURLCallerTaskInfo)
    autocomplete = 'off'

    def applyChanges(self, data):
        result = super(URLCallerTaskEditForm, self).applyChanges(data)
        if result:
            self.context.reset()
        return result


class URLCallerTaskEditFormMenu(DialogMenuItem):
    """URL caller task add form menu"""

    title = _(" :: URL properties...")
    target = URLCallerTaskEditForm
