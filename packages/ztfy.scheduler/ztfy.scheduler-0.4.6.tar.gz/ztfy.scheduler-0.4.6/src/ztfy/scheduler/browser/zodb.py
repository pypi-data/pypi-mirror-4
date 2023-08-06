### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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
from ztfy.scheduler.interfaces import IZODBPackingTaskInfo

# import Zope3 packages

# import local packages
from ztfy.scheduler.browser.task import BaseTaskAddForm
from ztfy.scheduler.zodb import ZODBPackingTask
from ztfy.skin.form import DialogEditForm
from ztfy.skin.menu import DialogMenuItem

from ztfy.scheduler import _


class ZODBPackingTaskAddForm(BaseTaskAddForm):
    """ZODB packing task add form"""

    task_factory = ZODBPackingTask


class ZODBPackingTaskAddFormMenu(DialogMenuItem):
    """ZODB packing task add form menu"""

    title = _(" :: Add ZODB packing task...")
    target = ZODBPackingTaskAddForm


class ZODBPackingTaskEditForm(DialogEditForm):
    """ZODB packer task edit form"""

    legend = _("Properties of ZEO packed database")

    fields = field.Fields(IZODBPackingTaskInfo)
    autocomplete = 'off'

    def applyChanges(self, data):
        result = super(ZODBPackingTaskEditForm, self).applyChanges(data)
        if result:
            self.context.reset()
        return result


class ZODBPackingTaskEditFormMenu(DialogMenuItem):
    """ZZODB packing task edit form menu"""

    title = _(" :: Packer properties...")
    target = ZODBPackingTaskEditForm
