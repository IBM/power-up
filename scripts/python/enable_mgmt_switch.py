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
import netaddr

from lib.inventory import Inventory
from lib.logger import Logger
from lib.switch import SwitchFactory
from lib.switch_exception import SwitchException

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class EnableMgmtSwitch(object):
    MAX_INTF = 128

    def __init__(self, log, inv_file):
        inv = Inventory(log, inv_file)
        self.log = log

        if inv.is_passive_mgmt_switches():
            self.log.info('Mode set for passive Management Switch(es)')
            sys.exit(0)

        for self.ipv4 in inv.yield_mgmt_switch_ip():
            pass
        self.vlan_mgmt = inv.get_vlan_mgmt_network()
        self.port_mgmt = inv.get_port_mgmt_network()
        self.userid = inv.get_userid_mgmt_switch()
        self.password = inv.get_password_mgmt_switch()
        self.switch_class = inv.get_mgmt_switch_class()
        mgmt_network = inv.get_ipaddr_mgmt_network()
        self.broadcast = str(netaddr.IPNetwork(mgmt_network).broadcast)
        self.mask = str(netaddr.IPNetwork(mgmt_network).netmask)

        self.ext_ip_dev = inv.get_mgmt_switch_external_dev_ip()
        self.ext_prefix = inv.get_mgmt_switch_external_prefix()
        for self.ext_ip_switch in inv.yield_mgmt_switch_external_switch_ip():
            pass

        self.ext_broadcast = str(netaddr.IPNetwork(
            self.ext_ip_dev + '/' + self.ext_prefix).broadcast)
        self.ext_mask = str(netaddr.IPNetwork(
            self.ext_ip_dev + '/' + self.ext_prefix).netmask)
        # self.vlan_client = inv.get_vlan_mgmt_client_network()

        sw = SwitchFactory.factory(
            log,
            self.switch_class,
            self.ext_ip_switch,
            self.userid,
            self.password,
            mode='active')

        if not sw.is_pingable():
            self.log.error('Management switch at address %s is not responding to pings' % self.ext_ip_switch)
            sys.exit(1)
        try:
            print('ipv4: ' + self.ipv4 + ' ' + self.mask + ' ' + str(self.vlan_mgmt))
            sw.configure_interface(self.ipv4, self.mask, self.vlan_mgmt)
        except SwitchException as exc:
            print(exc)
            self.log.error(exc)

        try:
            sw.add_vlans_to_port(self.port_mgmt, self.vlan_mgmt)
            print('Adding vlan %d to port %d' % (self.vlan_mgmt, self.port_mgmt))
        except SwitchException as exc:
            print(exc)
            self.log.error(exc)

        for port in inv.yield_ports_mgmt_data_network():
            try:
                print('Setting Native vlan to %s for port %s' % (self.vlan_mgmt, port))
                sw.set_switchport_native_vlan(self.vlan_mgmt, port)
            except SwitchException as exc:
                print(exc)
                self.log.error(exc)


if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: log level
    """
    LOG = Logger(__file__)

    if len(sys.argv) != 3:
        try:
            raise Exception()
        except Exception:
            LOG.error('Invalid argument count')
            sys.exit(1)

    INV_FILE = sys.argv[1]
    LOG.set_level(sys.argv[2])

    EnableMgmtSwitch(LOG, INV_FILE)
