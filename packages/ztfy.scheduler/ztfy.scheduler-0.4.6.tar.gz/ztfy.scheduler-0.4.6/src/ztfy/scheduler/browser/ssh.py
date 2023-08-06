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
from ztfy.scheduler.interfaces import ISSHCallerTaskInfo

# import Zope3 packages

# import local packages
from ztfy.scheduler.browser.task import BaseTaskAddForm
from ztfy.scheduler.ssh import SSHCallerTask
from ztfy.skin.form import DialogEditForm
from ztfy.skin.menu import DialogMenuItem

from ztfy.scheduler import _


class SSHCallerTaskAddForm(BaseTaskAddForm):
    """SSH caller add form"""

    task_factory = SSHCallerTask


class SSHCallerTaskAddFormMenu(DialogMenuItem):
    """SSH caller task add form menu"""

    title = _(" :: Add SSH command caller...")
    target = SSHCallerTaskAddForm


class SSHCallerTaskEditForm(DialogEditForm):
    """SSH caller task edit form"""

    fields = field.Fields(ISSHCallerTaskInfo)
    autocomplete = 'off'

    def applyChanges(self, data):
        result = super(SSHCallerTaskEditForm, self).applyChanges(data)
        if result:
            self.context.reset()
        return result


class SSHCallerTaskEditFormMenu(DialogMenuItem):
    """SSH caller task add form menu"""

    title = _(" :: SSH command properties...")
    target = SSHCallerTaskEditForm
