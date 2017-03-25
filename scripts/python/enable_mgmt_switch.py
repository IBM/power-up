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
    SET_INTERFACE_IPADDR = 'interface ip %d\nip address %s'
    SET_INTERFACE_MASK = 'interface ip %d\nip netmask %s'
    SET_INTERFACE_VLAN = 'interface ip %d\n' + SET_VLAN
    ENABLE_INTERFACE = 'interface ip %d\nenable'

    MAX_INTF = 128
    BRIDGE = 'bridge'
    LOCAL = 'lo'
    UP_STATE = 'up'

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
        self.broadcast = str(netaddr.IPNetwork(mgmt_network).broadcast)
        self.mask = str(netaddr.IPNetwork(mgmt_network).netmask)

        self.ext_label_dev = inv.get_mgmt_switch_external_dev_label()
        if self.ext_label_dev:
            self.log.debug(
                'External dev label %s was specified' % self.ext_label_dev)
        else:
            self.log.debug('External dev label was not specified')
        self.ext_ip_dev = inv.get_mgmt_switch_external_dev_ip()
        self.ext_prefix = inv.get_mgmt_switch_external_prefix()
        for self.ext_ip_switch in inv.yield_mgmt_switch_external_switch_ip():
            pass

        self.ext_broadcast = str(netaddr.IPNetwork(
            self.ext_ip_dev + '/' + self.ext_prefix).broadcast)
        self.ext_mask = str(netaddr.IPNetwork(
            self.ext_ip_dev + '/' + self.ext_prefix).netmask)

        self.ipr = IPRoute()
        for link in self.ipr.get_links():
            kind = None
            try:
                self.label = (link.get_attr('IFLA_IFNAME'))
                kind = (link.get_attr('IFLA_LINKINFO').get_attr(
                    'IFLA_INFO_KIND'))
            except:
                pass
            if kind == self.BRIDGE:
                if self.ipr.get_addr(
                        label=self.label, broadcast=self.broadcast):
                    self.log.info(
                        'Bridge %s on management subnet %s found' %
                        (self.label, mgmt_network))
                    if self._ping(self.ipv4, self.label):
                        self.log.info(
                            'Management switch found on %s' %
                            self.label)
                        sys.exit(0)
                    else:
                        self.log.debug(
                            'Management switch not found on %s' %
                            self.label)

        if self.ext_label_dev:
            self.dev = self.ipr.link_lookup(ifname=self.ext_label_dev)[0]
            self._add_ip()
            self._configure_switch()
            self._del_ip()

            # Print to stdout for Ansible playbook to register
            print(self.ext_label_dev)
        else:
            switch_found = False
            for link in self.ipr.get_links():
                kind = None
                try:
                    self.label = (link.get_attr('IFLA_IFNAME'))
                    kind = (link.get_attr('IFLA_LINKINFO').get_attr(
                        'IFLA_INFO_KIND'))
                except:
                    pass
                if self.label != self.LOCAL and not kind:
                    self.dev = self.ipr.link_lookup(ifname=self.label)[0]
                    self._add_ip()

                    if self._ping(self.ext_ip_switch, self.label):
                        switch_found = True
                        self.log.info(
                            'Management switch found on %s' %
                            self.label)
                        self._configure_switch()
                    else:
                        self.log.debug(
                            'Management switch not found on %s' % self.label)

                    self._del_ip()

                    if switch_found:
                        break

            if not switch_found:
                self.log.error('Management switch not found')
                sys.exit(1)

            # Print to stdout for Ansible playbook to register
            print(self.label)

    def __del__(self):
        self._del_ip()

    def _add_ip(self):
        if self.ext_label_dev:
            label = self.ext_label_dev
        else:
            label = self.label
        if self.ipr.get_addr(label=label, address=self.ext_ip_dev):
            self._is_add_ext_ip = False
            self.log.debug(
                '%s was already configured on %s' %
                (self.ext_ip_dev, label))
        else:
            self._is_add_ext_ip = True
            self.log.debug(
                'Add %s to interface %s' % (self.ext_ip_dev, label))
            self.ipr.addr(
                'add',
                index=self.dev,
                address=self.ext_ip_dev,
                mask=int(self.ext_prefix),
                broadcast=self.ext_broadcast)

    def _del_ip(self):
        if self.ext_label_dev:
            label = self.ext_label_dev
        else:
            label = self.label
        if self._is_add_ext_ip:
            self.log.debug(
                'Delete %s from interface %s' % (self.ext_ip_dev, label))
            self.ipr.addr(
                'delete',
                index=self.dev,
                address=self.ext_ip_dev,
                mask=int(self.ext_prefix),
                broadcast=self.ext_broadcast)
            self._is_add_ext_ip = False

    def _get_available_interface(self, interfaces):
        intf = 0
        while intf < self.MAX_INTF:
            intf += 1
            match = re.search(
                r'^%d:\s+IP4\s+' % intf,
                interfaces,
                re.MULTILINE)
            if match:
                continue
            return intf

        self.log.error('No available switch interface was found')
        sys.exit(1)

    def _configure_interface(self, intf):
        self._send_cmd(
            self.ext_ip_switch,
            self.SET_INTERFACE_IPADDR % (intf, self.ipv4),
            'Set IP %s on interface %d' % (self.ipv4, intf),
            False)

        self._send_cmd(
            self.ext_ip_switch,
            self.SET_INTERFACE_MASK % (intf, self.mask),
            'Set mask %s on interface %d' % (self.mask, intf),
            False)

        self._send_cmd(
            self.ext_ip_switch,
            self.SET_INTERFACE_VLAN % (intf, self.vlan_mgmt),
            'Set VLAN %d on interface %d' % (self.vlan_mgmt, intf),
            False)

        self._send_cmd(
            self.ext_ip_switch,
            self.ENABLE_INTERFACE % intf,
            'Enable interface %d' % intf,
            False)

    def _check_interface(self, intf, interfaces):
        match = re.search(
            r'^%d:\s+IP4\s+\S+\s+(\S+)\s+(\S+),\s+vlan\s(\S+),\s+(\S+)' % intf,
            interfaces,
            re.MULTILINE)
        if not match:
            self.log.error('Misconfigured switch interface %d' % intf)
            sys.exit(1)
        mask = match.group(1)
        broadcast = match.group(2)
        vlan = match.group(3)
        state = match.group(4)

        if mask != self.mask:
            self.log.error(
                'Invalid switch mask %s for interface %d' %
                (mask, intf))
            sys.exit(1)
        if vlan != str(self.vlan_mgmt):
            self.log.error(
                'Invalid switch VLAN %s for interface %d' %
                (vlan, intf))
            sys.exit(1)
        if broadcast != str(self.broadcast):
            self.log.error(
                'Invalid switch broadcast %s for interface %d' %
                (broadcast, intf))
            sys.exit(1)
        if state != self.UP_STATE:
            self.log.error(
                'Switch interface %d is %s' % (intf, state))
            sys.exit(1)

    def _configure_switch(self):
        self._send_cmd(
            self.ext_ip_switch,
            self.SET_VLAN % self.vlan_mgmt,
            'Create vlan %d' % self.vlan_mgmt,
            False)

        interfaces = str(self._send_cmd(
            self.ext_ip_switch, self.SHOW_INTERFACE_IP, '', False))
        match = re.search(
            r'^(\d+):\s+IP4\s+%s\s+' % self.ipv4,
            self._send_cmd(
                self.ext_ip_switch, self.SHOW_INTERFACE_IP, '', False),
            re.MULTILINE)
        if match:
            intf = int(match.group(1))
            self.log.info('Switch interface %d was found' % intf)
            self._check_interface(intf, interfaces)
        else:
            intf = self._get_available_interface(interfaces)
            self._configure_interface(intf)
            self.log.info('Switch interface %s created' % intf)

        self._send_cmd(
            self.ext_ip_switch,
            self.ADD_VLAN_TO_TRUNK_PORT % (self.port_mgmt, self.vlan_mgmt),
            'Set port %d to trunk mode and add vlan %d' %
            (self.port_mgmt, self.vlan_mgmt),
            False)

    def _ping(self, ipaddr, dev):
        if os.system('ping -c 1 -I %s %s > /dev/null' % (dev, ipaddr)):
            self.log.info(
                'Ping via %s to management switch at %s failed' %
                (dev, ipaddr))
            return False
        self.log.info(
            'Ping via %s to management switch at %s passed' %
            (dev, ipaddr))
        return True

    def _send_cmd(self, ipaddr, cmd, msg, status_check=True):
        ssh = SSH(self.log)
        self.log.debug('Switch cmd: ' + repr(cmd))
        status, stdout_, _ = ssh.exec_cmd(
            ipaddr,
            self.userid,
            self.password,
            self.ENABLE_REMOTE_CONFIG % cmd)
        if status:
            if status_check:
                self.log.error(
                    'Failed: ' + msg + ' on ' + ipaddr +
                    ' - Error: ' +
                    stdout_.replace('\n', ' ').replace('\r', ''))
                sys.exit(1)
            else:
                if msg:
                    self.log.info(
                        msg + ' on ' + ipaddr)
        else:
            if msg:
                self.log.info(msg + ' on ' + ipaddr)
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
