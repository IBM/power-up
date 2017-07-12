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
from orderedattrdict import AttrDict
from tabulate import tabulate
import os.path
import re

from lib.inventory import Inventory
from lib.logger import Logger
from get_dhcp_lease_info import GetDhcpLeases
from lib.switch import SwitchFactory
from lib.switch_common import SwitchCommon


class InventoryAddPorts(object):
    def __init__(self, dhcp_leases_file, log, inv_file, port_type):
        inv = Inventory(log, inv_file)

        dhcp_leases = GetDhcpLeases(dhcp_leases_file, log)
        dhcp_mac_ip = dhcp_leases.get_mac_ip()

        mgmt_sw_cfg_mac_lists = AttrDict()
        if inv.is_passive_mgmt_switches():
            for rack, switch_ip in inv.yield_mgmt_rack_ipv4():
                scripts_path = os.path.abspath(__file__)
                playbooks_path = (
                    re.match('(.*cluster\-genesis).*', scripts_path).group(1) +
                    '/passive/')
                file_path = playbooks_path + switch_ip
                mac_info = {}
                try:
                    with open(file_path, 'r') as f:
                        mac_info = f.read()

                except IOError as error:
                    self.log.error(
                        'Passive switch MAC address table file not found (%s)' % error)
                    raise
                mgmt_sw_cfg_mac_lists[rack] = SwitchCommon.get_port_to_mac(mac_info, log)
        else:
            switch_class = inv.get_mgmt_switch_class()
            userid = inv.get_userid_mgmt_switch()
            password = inv.get_password_mgmt_switch()
            for rack, ipv4 in inv.yield_mgmt_rack_ipv4():
                sw = SwitchFactory.factory(
                    log,
                    switch_class,
                    ipv4,
                    userid,
                    password,
                    mode='active')
                mgmt_sw_cfg_mac_lists[rack] = sw.show_mac_address_table(format='std')

        if port_type == "ipmi":
            inv.create_nodes(dhcp_mac_ip, mgmt_sw_cfg_mac_lists)
        elif port_type == "pxe":
            inv.add_pxe(dhcp_mac_ip, mgmt_sw_cfg_mac_lists)

        self.table = []

        ports_total = 0
        ports_found = 0
        for template, rack, ports in inv.yield_template_ports(port_type):
            for port in ports:
                ports_total += 1
                result = inv.check_port(template, port_type, rack, port)
                if result:
                    ports_found += 1
                    self.table.append(
                        [True, template, port_type, rack, port, result[0],
                         result[1]])
                    log.info(
                        'Node Port Defined in Inventory - Template: %s '
                        'Type: %s Rack: %s Port: %02d MAC: %s IP: %s' %
                        (template, port_type, rack, port, result[0],
                         result[1]))
                elif str(port) in mgmt_sw_cfg_mac_lists[rack]:
                    for mac in mgmt_sw_cfg_mac_lists[rack][str(port)]:
                        if mac in dhcp_mac_ip:
                            ipaddr = dhcp_mac_ip[mac]
                            self.table.append(
                                [False, template, port_type, rack, port, mac,
                                 ipaddr])
                            log.warning(
                                'Node Port MAC/IP NOT Defined in Inventory - '
                                'Template: %s Type: %s Rack: %s Port: %02d '
                                'MAC: %s IP: %s' %
                                (template, port_type, rack, port, mac, ipaddr))
                        else:
                            self.table.append(
                                [False, template, port_type, rack, port, mac,
                                 '-'])
                            log.warning(
                                'No DHCP Lease Found for Port MAC Address - '
                                'Template: %s Type: %s Rack: %s Port: %02d '
                                'MAC: %s' %
                                (template, port_type, rack, port, mac))
                else:
                    self.table.append(
                        [False, template, port_type, rack, port, '-', '-'])
                    log.warning(
                        'No Entries Found in MGMT Switch MAC Address Table - '
                        'Template: %s Type: %s Rack: %s Port: %02d' %
                        (template, port_type, rack, port))

        self.table.append(['----------------'])
        if ports_found == ports_total:
            self.table.append(['Complete!'])
            log.info('Found: %d/%d nodes' % (ports_found, ports_total))
        else:
            self.table.append(['INCOMPLETE!'])
            log.warning('Found: %d/%d nodes' % (ports_found, ports_total))
        self.table.append(['Found: %d/%d nodes' % (ports_found, ports_total)])

    def get_table(self):
        return self.table

    def get_table_pretty(self):
        table_header = ['In-Inventory', 'Template', 'Port Type', 'Rack',
                        'Port', 'MAC', 'IP']
        table_pretty = (tabulate(self.table, table_header))

        return table_pretty

    def get_table_status(self):
        for item in self.table:
            if item[0] is False:
                return False
        return True


if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: DHCP leases file
    Arg3: Port Type
    Arg4: log level
    """
    LOG = Logger(__file__)

    if len(sys.argv) != 5:
        try:
            raise Exception()
        except:
            LOG.error('Invalid argument count')
            sys.exit(1)

    INV_FILE = sys.argv[1]
    DHCP_LEASES_FILE = sys.argv[2]
    PORT_TYPE = sys.argv[3]
    LOG.set_level(sys.argv[4])

    INV_PORTS = InventoryAddPorts(
        DHCP_LEASES_FILE, LOG, INV_FILE, PORT_TYPE)

    print(INV_PORTS.get_table_pretty())
