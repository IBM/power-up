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

from lib.SwitchException import SwitchException
from lib.switch import SwitchFactory
from lib.inventory import Inventory
from lib.logger import Logger
from write_switch_memory import WriteSwitchMemory

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class ConfigureMgmtSwitch(object):
    SWITCH_PORT = 22

    DEBUG = b'debug'
    INFO = b'info'
    SSH_LOG = 'mgmt-switch-ssh.log'

#    SHOW_VLAN = 'show vlan %d'
#    SHOW_INTERFACE_TRUNK = 'show interface trunk | include %d'
#    SHOW_VLANS = 'show interface port %d | include VLANs'
#
#    ENABLE_REMOTE_CONFIG = 'enable;configure terminal; %s'
#    SET_VLAN = 'vlan %d'
#    ADD_VLAN_TO_TRUNK_PORT = (
#        'interface port %d'
#        ';switchport mode trunk'
#        ';switchport trunk allowed vlan add %d')
#    ADD_VLAN_TO_ACCESS_PORT = (
#        'interface port %d'
#        ';switchport access vlan %d')

    def __init__(self, log, inv_file):
        inv = Inventory(log, inv_file)
        self.log = log

        for self.ipv4 in inv.yield_mgmt_switch_ip():
            pass
        self.vlan_mgmt = inv.get_vlan_mgmt_network()
        self.vlan_mgmt_client = inv.get_vlan_mgmt_client_network()
        self.mgmt_port = inv.get_port_mgmt_network()
        self.userid = inv.get_userid_mgmt_switch()
        self.password = inv.get_password_mgmt_switch()
        self.switch_name = inv.get_mgmt_switch_name()
        self.switch = SwitchFactory.factory(
            log,
            self.switch_name,
            self.ipv4,
            self.userid,
            self.password,
            mode='active')

        # Check that management port is in trunc mode
        if self.switch.is_port_in_trunk_mode(self.mgmt_port):
            self.log.info(
                'Port %s is already in trunk mode' % (self.mgmt_port))
        else:
            self.log.error('Port %s is not in trunk mode' % (self.mgmt_port))
            sys.exit(1)

        # Check that management VLAN is added to management port
        if self.switch.is_vlan_allowed_for_port(self.vlan_mgmt, self.mgmt_port):
            self.log.info(
                'Management VLAN %s is already added to trunk port %s' %
                (self.vlan_mgmt, self.mgmt_port))
        else:
            self.log.error(
                'Management VLAN %s is not added to trunk port %s' %
                (self.vlan_mgmt, self.mgmt_port))
            sys.exit(1)

        # Set native vlan for management connections to data switch
        for mgmt_data_port in inv.yield_ports_mgmt_data_network():
            if self.vlan_mgmt == self.show_native_vlan(mgmt_data_port):
                self.log.info(
                    'Management VLAN %s is already set foR access port %s' %
                    (self.vlan_mgmt, mgmt_data_port))
            else:
                try:
                    self.switch.set_switchport_native_vlan(
                        self.vlan_mgmt, mgmt_data_port)
                except SwitchException as se:
                    self.log.error(se.message)
                    sys.exit(1)

        # Create management client VLAN
        if self.switch.is_vlan_created(self.vlan_mgmt_client):
            self.log.info(
                'Management client VLAN %s is already created' %
                (self.vlan_mgmt_client))
        else:
            try:
                self.switch.create_vlan(self, self.vlan_mgmt_client)
            except SwitchException as se:
                self.log.error(se.message)
                sys.exit(1)

        # Add management client VLAN to management port
        if self.switch.is_vlan_allowed_for_port(self.vlan_mgmt_client, self.mgmt_port):
            self.log.info(
                'Management VLAN %s is already added to trunk port %s' %
                (self.vlan_mgmt_client, self.mgmt_port))
        else:
            try:
                self.switch.add_vlan_to_trunk_port(self, self.vlan_mgmt_client, self.mgmt_port)
            except SwitchException as se:
                self.log.error(se.message)
                sys.exit(1)

        # For each management client port
        for port in inv.yield_mgmt_switch_ports():
            # Check that management client port is in access mode
            if self.switch.is_port_in_access_mode(port):
                self.log.info('Port %s is already in access mode' % (port))
            else:
                self.log.error('Port %s is not in access mode' % (port))
                sys.exit(1)

            # Add management client VLAN to port
            if self.vlan_mgmt_client == self.switch.show_native_vlan(port):
                self.log.info(
                    'Management VLAN %s is already added to access port %s' %
                    (self.vlan_mgmt_client, port))
            else:
                self.switch.set_switchport_native_vlan(self, self.vlan_mgmt_client, port)

        if inv.is_write_switch_memory():
            switch_mem = WriteSwitchMemory(LOG, INV_FILE)
            switch_mem.write_mgmt_switch_memory()


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

    ConfigureMgmtSwitch(LOG, INV_FILE)
