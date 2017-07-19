#!/usr/bin/env python
# Copyright 2017 IBM Corp.
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


class SSH_Exception(Exception):
    pass


class SSH(object):
    SWITCH_PORT = 22
    SSH_LOG = FILE_PATH + '_ssh.log'

    def __init__(self, log):
        self.log = log

    def exec_cmd(self, ip_addr, username, password, cmd,
                 ssh_log=None, look_for_keys=True, key_filename=None):
        if ssh_log is not None:
            self.SSH_LOG = ssh_log
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
                password=password,
                look_for_keys=look_for_keys,
                key_filename=key_filename)
        except (
                paramiko.BadHostKeyException,
                paramiko.AuthenticationException,
                paramiko.SSHException,
                socket.error,
                BaseException) as exc:
            self.log.error('%s: %s' % (ip_addr, str(exc)))
            raise SSH_Exception('SSH connection Failure - {}'.format(exc))
            # sys.exit(1)
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


class SSH_CONNECTION(paramiko.SSHClient):
    """Returns a connected paramiko SSHClient
    Use send_cmd to run paramiko exec_command with additional error handling
    Application must close the connection with paramiko close()

    Args:
        host (string): host ip address or name (paramiko hostname)
        log (Logger object): Logging.
        ssh_log (string): filepath for paramiko log
        see paramiko documentation for other args
    """

    def __init__(self, host, log=None, ssh_log=None, username=None,
                 password=None, look_for_keys=True, key_filename=None):
        paramiko.SSHClient.__init__(self)
        self.host = host
        self.log = log
        self.ssh_log = ssh_log
        if ssh_log is not None:
            paramiko.util.log_to_file(ssh_log)
        elif log is not None:
            if self.log.get_level() == Logger.DEBUG:
                ssh_log = FILE_PATH[:FILE_PATH.rfind('/')]
                ssh_log += '/ssh_paramiko.log'
                paramiko.util.log_to_file(ssh_log)
        if key_filename is None:
            self.load_system_host_keys()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.connect(
                host,
                username=username,
                password=password,
                look_for_keys=look_for_keys,
                key_filename=key_filename)
        except (
                paramiko.BadHostKeyException,
                paramiko.AuthenticationException,
                paramiko.SSHException,
                socket.error,
                BaseException) as exc:
            if log is not None:
                self.log.error('%s: %s' % (host, str(exc)))
            else:
                print('%s: %s' % (host, str(exc)))
            raise SSH_Exception('Connection Failure - {}'.format(exc))

    def send_cmd(self, cmd):
        try:
            _, stdout, stderr = self.exec_command(cmd)
        except paramiko.SSHException as exc:
            if self.log is not None:
                self.log.error('%s: %s' % (self.host, str(exc)))
            else:
                print('%s: %s' % (self.host, str(exc)))
            sys.exit(1)
        stdout_ = stdout.read()
        stderr_ = stderr.read()
        status = stdout.channel.recv_exit_status()
        return status, stdout_, stderr_
