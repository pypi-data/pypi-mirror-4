### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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
import os
import paramiko
from paramiko.ssh_exception import SSHException
import subprocess
import sys
import traceback

# import Zope3 interfaces

# import local interfaces
from ztfy.scheduler.interfaces import ISSHCallerTask

# import Zope3 packages
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.scheduler.task import BaseTask


class SSHCallerTask(BaseTask):
    """SSH caller task"""

    implements(ISSHCallerTask)

    hostname = FieldProperty(ISSHCallerTask['hostname'])
    port = FieldProperty(ISSHCallerTask['port'])
    username = FieldProperty(ISSHCallerTask['username'])
    private_key = FieldProperty(ISSHCallerTask['private_key'])
    password = FieldProperty(ISSHCallerTask['password'])
    cmdline = FieldProperty(ISSHCallerTask['cmdline'])

    def run(self, report):
        if self.hostname:
            self._runRemote(report)
        else:
            self._runLocal(report)

    def _runRemote(self, report):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, self.port, self.username, self.password,
                    key_filename=os.path.expanduser(self.private_key) if self.private_key else None)
        try:
            stdin, stdout, stderr = ssh.exec_command(self.cmdline)
            stdin.close()
            report.write(stdout.read())
            errors = stderr.read()
            if errors:
                report.write('\n\nSome errors occured\n===================\n')
                report.write(errors)
        except SSHException:
            etype, value, tb = sys.exc_info()
            report.write('\n\nAn error occured\n================\n')
            report.write(''.join(traceback.format_exception(etype, value, tb)))

    def _runLocal(self, report):
        shell = subprocess.Popen(self.cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdin, stdout = shell.communicate()
        report.write(stdin)
        if stdout:
            report.write('\n\nSome errors occured\n===================\n')
            report.write(stdout)
