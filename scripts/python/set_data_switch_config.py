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

from lib.inventory import Inventory
from lib.logger import Logger
from lib.ssh import SSH

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class ConfigureDataSwitch(object):
    ENABLE_REMOTE_CONFIG = 'cli enable "configure terminal" %s'
    SET_VLAN = '"vlan %d"'
    SET_MTU = '"mtu %d"'
    INTERFACE_ETHERNET = '"interface ethernet 1/%s"'
    SWITCHPORT_MODE_HYBRID = '"switchport mode hybrid"'
    SWITCHPORT_HYBRID_ALLOWED_VLAN = \
        '"switchport hybrid allowed-vlan add %d"'
    SHUTDOWN = '"shutdown"'
    NO_SHUTDOWN = '"no shutdown"'

    def __init__(self, log_level, inv_file):

        self.log = Logger(__file__)
        self.log_level = log_level
        if log_level is not None:
            self.log.set_level(log_level)

        inv = Inventory(log_level, inv_file)

        for self.ipv4, self.userid, self.password, vlans \
                in inv.yield_data_vlans():
            for vlan in vlans:
                status_ok, msg = self.send_cmd(self.SET_VLAN % vlan)
                if status_ok:
                    self.log.info('Create vlan %s' % vlan)
                else:
                    self.log.error(
                        'Failed to create vlan %s' % vlan +
                        ' - Error: ' + msg)
                    exit(1)

        for self.ipv4, self.userid, self.password, port_vlans, port_mtu \
                in inv.yield_data_switch_ports():
            for port, vlans in port_vlans.items():
                status_ok, msg = self.send_cmd(
                    self.INTERFACE_ETHERNET % port +
                    ' ' +
                    self.SWITCHPORT_MODE_HYBRID)
                if status_ok:
                    self.log.info(
                        'Enable hybrid mode for port %s' % port)
                else:
                    self.log.error(
                        'Failed to enable hybrid mode for port %s' % port +
                        ' - Error: ' + msg)
                    exit(1)
                for vlan in vlans:
                    status_ok, msg = self.send_cmd(
                        self.INTERFACE_ETHERNET % port +
                        ' ' +
                        self.SWITCHPORT_HYBRID_ALLOWED_VLAN % vlan)
                    if status_ok:
                        self.log.info(
                            'Add vlan %s to port %s in hybrid mode' %
                            (vlan, port))
                    else:
                        self.log.error(
                            'Failed to add vlan %s to port %s in hybrid mode' %
                            (vlan, port) + ' - Error: ' + msg)
                        exit(1)
            for port, mtu in port_mtu.items():
                status_ok, msg = self.send_cmd(
                    self.INTERFACE_ETHERNET % port +
                    ' ' +
                    self.SHUTDOWN)
                if status_ok:
                    self.log.info('Shut down port %s' % port)
                else:
                    self.log.error(
                        'Failed to shut down port %s' % port +
                        ' - Error: ' + msg)
                    exit(1)

                status_ok, msg = self.send_cmd(
                    self.INTERFACE_ETHERNET % port +
                    ' ' +
                    self.SET_MTU % mtu)
                if status_ok:
                    self.log.info(
                        'Port %s mtu set to %s' % (port, mtu))
                else:
                    self.log.error(
                        'Failed to set port %s mtu to %s' %
                        (port, mtu) + ' - Error: ' + msg)
                    exit(1)

                status_ok, msg = self.send_cmd(
                    self.INTERFACE_ETHERNET % port +
                    ' ' +
                    self.NO_SHUTDOWN)
                if status_ok:
                    self.log.info(
                        'Bring up port %s' % port)
                else:
                    self.log.error(
                        'Failed to bring up port %s' % port +
                        ' - Error: ' + msg)
                    exit(1)

    def send_cmd(self, cmd):
        ssh = SSH(self.log)
        status, stdout_, _ = ssh.exec_cmd(
            self.ipv4,
            self.userid,
            self.password,
            self.ENABLE_REMOTE_CONFIG % cmd)
        stdout_ = stdout_.replace('\n', ' ').replace('\r', '')
        if status:
            return False, stdout_
        return True, stdout_

if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: log level
    """
    LOG = Logger(__file__)

    ARGV_MAX = 3
    ARGV_COUNT = len(sys.argv)
    if ARGV_COUNT > ARGV_MAX:
        try:
            raise Exception()
        except:
            LOG.error('Invalid argument count')
            exit(1)

    LOG.clear()

    INV_FILE = sys.argv[1]
    if ARGV_COUNT == ARGV_MAX:
        LOG_LEVEL = sys.argv[2]
    else:
        LOG_LEVEL = None

    ConfigureDataSwitch(LOG_LEVEL, INV_FILE)
