#!/usr/bin/env python
# Copyright 2016 IBM Corp.
#
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals

import sys
import os.path
import socket
import paramiko

from lib.logger import Logger

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class SSH(object):
    SWITCH_PORT = 22
    SSH_LOG = FILE_PATH + '_ssh.log'

    def __init__(self, log):
        self.log = log

    def exec_cmd(self, ip_addr, username, password, cmd):
        if self.log.get_level() == Logger.DEBUG:
            paramiko.util.log_to_file(self.SSH_LOG)
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                ip_addr,
                port=self.SWITCH_PORT,
                username=username,
                password=password)
        except (
                paramiko.BadHostKeyException,
                paramiko.AuthenticationException,
                paramiko.SSHException,
                socket.error,
                BaseException) as exc:
            self.log.error('%s: %s' % (ip_addr, str(exc)))
            sys.exit(1)
        try:
            _, stdout, stderr = ssh.exec_command(cmd)
        except paramiko.SSHException as exc:
            self.log.error('%s: %s, %s' % (ip_addr, str(exc), stderr.read()))
            sys.exit(1)
        stdout_ = stdout.read()
        stderr_ = stderr.read()
        status = stdout.channel.recv_exit_status()
        ssh.close()
        return status, stdout_, stderr_
