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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.scheduler.interfaces import IZODBPackingTask
from ztfy.utils.interfaces import IZEOConnection

# import Zope3 packages
from zope.component import queryUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.scheduler.task import BaseTask


class ZODBPackingTask(BaseTask):
    """ZODB packing task"""

    implements(IZODBPackingTask)

    zeo_connection = FieldProperty(IZODBPackingTask['zeo_connection'])
    pack_time = FieldProperty(IZODBPackingTask['pack_time'])

    def run(self, report):
        zeo_connection = queryUtility(IZEOConnection, self.zeo_connection)
        if zeo_connection is None:
            report.write("No ZEO connection. Task aborted.")
            return
        report.write("ZEO connection name = %s\n" % self.zeo_connection)
        report.write("Packing transactions older than %d days\n" % self.pack_time)
        storage, db = zeo_connection.getConnection(get_storage=True)
        try:
            db.pack(days=self.pack_time)
            report.write("\nPack successful.\n")
        finally:
            storage.close()
