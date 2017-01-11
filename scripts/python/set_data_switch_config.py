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
import paramiko

from lib.inventory import Inventory
from lib.logger import Logger

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class ConfigureDataSwitch(object):
    def __init__(self, log_level, inv_file):
        self.SWITCH_PORT = 22

        self.DEBUG = b'DEBUG'
        self.INFO = b'INFO'
        self.SSH_LOG = 'data-switch-ssh.log'

        self.ENABLE_REMOTE_CONFIG = 'cli enable \"configure terminal\" %s'
        SET_VLAN = '\"vlan %d\"'
        SET_MTU = '\"mtu %d\"'
        INTERFACE_ETHERNET = '\"interface ethernet 1/%s\"'
        SWITCHPORT_MODE_HYBRID = '\"switchport mode hybrid\"'
        SWITCHPORT_HYBRID_ALLOWED_VLAN = \
            '\"switchport hybrid allowed-vlan add %d\"'
        SHUTDOWN = '"shutdown"'
        NO_SHUTDOWN = '"no shutdown"'

        self.log = Logger(__file__)
        self.log_level = log_level
        if log_level is not None:
            log.set_level(log_level)

        inv = Inventory(log_level, inv_file)

        for self.ipv4, self.userid, self.password, vlans \
                in inv.yield_data_vlans():
            for vlan in vlans:
                self.log.info('Create vlan %s' % (vlan))
                self.issue_cmd(SET_VLAN % (vlan))

        for self.ipv4, self.userid, self.password, port_vlans, port_mtu \
                in inv.yield_data_switch_ports():
            for port, vlans in port_vlans.items():
                self.log.info(
                    'Enable hybrid mode for port %s' % (port))
                self.issue_cmd(
                    INTERFACE_ETHERNET % (port) +
                    ' ' +
                    SWITCHPORT_MODE_HYBRID)
                for vlan in vlans:
                    self.log.info(
                        'In hybrid mode add vlan %s to port %s' %
                        (vlan, port))
                    self.issue_cmd(
                        INTERFACE_ETHERNET % (port) +
                        ' ' +
                        SWITCHPORT_HYBRID_ALLOWED_VLAN % (vlan))
            for port, mtu in port_mtu.items():
                self.log.info(
                    'Port %s mtu set to %s' %
                    (port, mtu))
                self.issue_cmd(
                    INTERFACE_ETHERNET % (port) +
                    ' ' +
                    SHUTDOWN)
                self.issue_cmd(
                    INTERFACE_ETHERNET % (port) +
                    ' ' +
                    SET_MTU % (mtu))
                self.issue_cmd(
                    INTERFACE_ETHERNET % (port) +
                    ' ' +
                    NO_SHUTDOWN)

    def issue_cmd(self, cmd):
        if self.log_level == self.DEBUG or self.log_level == self.INFO:
            paramiko.util.log_to_file(self.SSH_LOG)
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(
            self.ipv4,
            self.SWITCH_PORT,
            self.userid,
            self.password)
        stdin, stdout, stderr = s.exec_command(
            self.ENABLE_REMOTE_CONFIG % (cmd))
        # print(stdout.read())
        s.close()

if __name__ == '__main__':
    log = Logger(__file__)

    ARGV_MAX = 3
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    log.clear()

    inv_file = sys.argv[1]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[2]
    else:
        log_level = None

    ipmi_data = ConfigureDataSwitch(log_level, inv_file)
