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
import re
import netaddr
from pyroute2 import IPRoute

from lib.inventory import Inventory
from lib.logger import Logger
from lib.ssh import SSH

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class EnableMgmtSwitch(object):
    ENABLE_REMOTE_CONFIG = 'enable\nconfigure terminal\n%s'
    SET_VLAN = 'vlan %d'
    ADD_VLAN_TO_TRUNK_PORT = (
        'interface port %d'
        '\nswitchport mode trunk'
        '\nswitchport trunk allowed vlan add %d')
    SHOW_INTERFACE_IP = 'show interface ip'
    SET_INTERFACE_VLAN = 'interface ip %d' + '\n' + SET_VLAN

    BRIDGE = 'bridge'
    LOCAL = 'lo'

    def __init__(self, log_level, inv_file):
        self.log = Logger(__file__)
        self.log_level = log_level
        if log_level is not None:
            self.log.set_level(log_level)

        inv = Inventory(log_level, inv_file)

        for self.ipv4 in inv.yield_mgmt_switch_ip():
            pass
        self.vlan_mgmt = inv.get_vlan_mgmt_network()
        self.port_mgmt = inv.get_port_mgmt_network()
        self.userid = inv.get_userid_mgmt_switch()
        self.password = inv.get_password_mgmt_switch()

        mgmt_network = inv.get_ipaddr_mgmt_network()
        broadcast = str(netaddr.IPNetwork(mgmt_network).broadcast)
        addr = str(netaddr.IPNetwork(mgmt_network)[0] + 1)
        mask = netaddr.IPNetwork(mgmt_network).prefixlen

        ipr = IPRoute()
        for link in ipr.get_links():
            kind = None
            try:
                label = (link.get_attr('IFLA_IFNAME'))
                kind = (link.get_attr('IFLA_LINKINFO').get_attr(
                    'IFLA_INFO_KIND'))
            except:
                pass
            if kind == self.BRIDGE:
                if ipr.get_addr(label=label, broadcast=broadcast):
                    self.log.info(
                        'Bridge %s on management subnet %s was found' %
                        (label, mgmt_network))
                    if self._ping(label):
                        self.log.info(
                            'Management switch found on %s' %
                            label)
                        sys.exit(0)
                    else:
                        self.log.debug(
                            'Management switch not found on %s' %
                            label)

        switch_found = False
        for link in ipr.get_links():
            kind = None
            try:
                label = (link.get_attr('IFLA_IFNAME'))
                kind = (link.get_attr('IFLA_LINKINFO').get_attr(
                    'IFLA_INFO_KIND'))
            except:
                pass
            if label != self.LOCAL and not kind:
                dev = ipr.link_lookup(ifname=label)[0]
                ipr.addr(
                    'add', index=dev,
                    address=addr, mask=mask,
                    broadcast=broadcast)
                self.log.debug('Add %s to interface %s' % (addr, label))

                if self._ping(label):
                    switch_found = True
                    self.log.info(
                        'Management switch found on %s' %
                        label)
                    self._configure_switch()
                else:
                    self.log.debug('Management switch not found on %s' % label)

                ipr.addr(
                    'delete', index=dev,
                    address=addr, mask=mask,
                    broadcast=broadcast)
                self.log.debug('Delete %s from interface %s' % (addr, label))

                if switch_found:
                    break

        if not switch_found:
            self.log.error('Management switch not found')
            sys.exit(1)

        # Print to stdout for Ansible playbook to register
        print(label)

    def _configure_switch(self):
        self._send_cmd(
            self.SET_VLAN % self.vlan_mgmt,
            'Create vlan %d' % self.vlan_mgmt,
            False)

        self._send_cmd(
            self.ADD_VLAN_TO_TRUNK_PORT % (self.port_mgmt, self.vlan_mgmt),
            'Set port %d to trunk mode and add vlan %d' %
            (self.port_mgmt, self.vlan_mgmt),
            False)

        pattern = re.compile(
            r'^(\d+):\s+IP4\s+' + self.ipv4 + r'\s+', re.MULTILINE)
        match = pattern.search(
            self._send_cmd(self.SHOW_INTERFACE_IP, '', False))
        if match:
            intf = int(match.group(1))
            self.log.debug('Switch interface was found on port %d' % intf)
        else:
            self.log.debug('Switch interface port was not found')
            sys.exit(1)

        self._send_cmd(
            self.SET_INTERFACE_VLAN % (intf, self.vlan_mgmt),
            'Set VLAN %d on interface %d' % (self.vlan_mgmt, intf),
            False)

    def _ping(self, label):
        if os.system('ping -c 1 ' + self.ipv4 + ' > /dev/null'):
            self.log.info(
                'Ping check via %s to management switch at %s failed' %
                (label, self.ipv4))
            return False
        self.log.info(
            'Ping check via %s to management switch at %s passed' %
            (label, self.ipv4))
        return True

    def _send_cmd(self, cmd, msg, status_check=True):
        ssh = SSH(self.log)
        self.log.debug('Switch cmd: ' + repr(cmd))
        status, stdout_, _ = ssh.exec_cmd(
            self.ipv4,
            self.userid,
            self.password,
            self.ENABLE_REMOTE_CONFIG % cmd)
        if status:
            if status_check:
                self.log.error(
                    'Failed: ' + msg + ' on ' + self.ipv4 +
                    ' - Error: ' +
                    stdout_.replace('\n', ' ').replace('\r', ''))
                sys.exit(1)
            else:
                if msg:
                    self.log.info(
                        msg + ' on ' + self.ipv4)
        else:
            if msg:
                self.log.info(msg + ' on ' + self.ipv4)
        return stdout_


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
        except Exception:
            LOG.error('Invalid argument count')
            sys.exit(1)

    LOG.clear()

    INV_FILE = sys.argv[1]
    if ARGV_COUNT == ARGV_MAX:
        LOG_LEVEL = sys.argv[2]
    else:
        LOG_LEVEL = None

    EnableMgmtSwitch(LOG_LEVEL, INV_FILE)
