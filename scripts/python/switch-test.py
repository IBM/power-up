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
import re

from lib.logger import Logger
from lib.switch import SwitchFactory
from lib.switch_exception import SwitchException
from lib.switch_common import SwitchCommon
from lib.genesis import gen_passive_path


def _get_available_interface(interfaces):
    intf = 0
    while intf < MAX_INTF:
        intf += 1
        match = re.search(
            r'^%d:\s+IP4\s+' % intf,
            interfaces,
            re.MULTILINE)
        if match:
            continue
        return intf


def print_dict(dict):
    if not dict:
        print('{}')
    for key in dict.keys():
        print(key.ljust(10) + ' ' + str(dict[key]))
    print()


MAX_INTF = 128

mellanox = (
    'Vlan    Mac Address         Type         Port\n'
    '----    -----------         ----         ------------\n'
    '1       7C:FE:90:A5:1A:B0   Dynamic      Eth1/17\n'
    '1       7C:FE:90:A5:1A:B1   Dynamic      Po6\n'
    '1       7C:FE:90:A5:1C:A0   Dynamic      Po6\n'
    '1       7C:FE:90:A5:24:30   Dynamic      Eth1/15\n'
    '1       7C:FE:90:A5:24:31   Dynamic      Po6\n'
    '1       7C:FE:90:A5:1A:B6   Dynamic      Eth1/17\n')

lenovo = (
    '     MAC address       VLAN     Port    Trnk  State  Permanent  Openflow\n'
    '  -----------------  --------  -------  ----  -----  ---------  --------\n'
    '  00:16:3e:96:bf:27      20    18             FWD                  N\n'
    '  00:16:3e:e8:45:fc      20    17             FWD                  N\n'
    '  0c:c4:7a:51:eb:13       1    17             FWD                  N\n')

cisco = (
    'Vlan    Mac Address       Type        Ports\n'
    '----    -----------       --------    -----\n'
    'All    0100.0ccc.cccc    STATIC      CPU\n'
    'All    0100.0ccc.cccc    STATIC      CPU\n'
    'All    0180.c200.0000    STATIC      CPU\n'
    '   1    000a.b82d.10e0    DYNAMIC     Fa0/16\n'
    '   1    0012.80b6.4cd8    DYNAMIC     Fa0/3\n'
    '   1    0012.80b6.4cd9    DYNAMIC     Fa0/16\n'
    '   4    0018.b974.528f    DYNAMIC     Fa0/16\n'
    'Total Mac Addresses for this criterion: 42 ')

empty = (
    'Vlan    Mac Address       Type        Ports\n'
    '----    -----------       --------    -----\n')


def main(log):
    print('Test the get_mac_dict static method in SwitchCommon')
    mac_dict = SwitchCommon.get_mac_dict(mellanox)
    print_dict(mac_dict)
    mac_test = mac_dict['Po6'] == [u'7C:FE:90:A5:1A:B1', u'7C:FE:90:A5:1C:A0', u'7C:FE:90:A5:24:31']
    if not mac_test:
        print('MAC test failed')
    else:
        print('MAC test passed')

    print('Test the get_port_to_mac static method in SwitchCommon')
    print('Test Mellanox format;')
    mac_dict = SwitchCommon.get_port_to_mac(mellanox, log)
    print_dict(mac_dict)
    print('Test Cisco format')
    mac_dict = SwitchCommon.get_port_to_mac(cisco, log)
    print_dict(mac_dict)

    sw = SwitchFactory.factory(log, 'lenovo', '192.168.32.20', 'admin', 'admin', mode='active')
    print('Is pingable: ' + str(sw.is_pingable()))

    print('Get mac address table in standard format: ')
    mac_dict = sw.show_mac_address_table(format='std')
    print_dict(mac_dict)

    print('Test Get mac address table in passive mode, standard format')
    filepath = gen_passive_path + '/mellanox_mac.txt'
    print(filepath)
    sw2 = SwitchFactory.factory(log, 'lenovo', host=filepath, mode='passive')
    mac_dict = sw2.show_mac_address_table(format='std')
    print_dict(mac_dict)

    # Test create and delete vlan
    print(sw.show_vlans())
    vlan_num = 999
    if sw.is_vlan_created(vlan_num):
        print('Deleting existing vlan {}'.format(vlan_num))
        sw.delete_vlan(vlan_num)
    print('Creating vlan {}'.format(vlan_num))
    try:
        sw.create_vlan(vlan_num)
    except SwitchException as exc:
        print (exc)
    print('Is vlan {} created? {}'.format(vlan_num, sw.is_vlan_created(vlan_num)))
    print('Deleting vlan {}'.format(vlan_num))
    sw.delete_vlan(vlan_num)
    print('Is vlan {} created? {}'.format(vlan_num, sw.is_vlan_created(vlan_num)))

    print('Port 18 in trunk mode: ' + str(sw.is_port_in_trunk_mode(18)))

    # test configure specific interface
    ifc_info = sw.show_mgmt_interfaces()
    print(ifc_info)

#    if '55: ' in ifc_info:
#        print('Interface 55 already in use')
#        exit(1)
#    print('Configure mgmt interface 55: ')
#    try:
#        sw.configure_mgmt_interface('192.168.17.17', '255.255.255.0', vlan=17, intf=55)
#        print(sw.show_mgmt_interfaces())
#        sw.remove_mgmt_interface(55)
#    except (SwitchException) as exc:
#        print(exc)
#
#    # test configure next available interface
#    print('Finding next available interface')
#    ifc_info = sw.show_mgmt_interfaces()
#    ifc = _get_available_interface(ifc_info)
#    print('Next available interface %d' % ifc)
#    try:
#        sw.configure_mgmt_interface('192.168.18.18', '255.255.255.0', vlan=18)
#        print(sw.show_mgmt_interfaces())
#        sw.remove_mgmt_interface(ifc)
#        print(sw.show_mgmt_interfaces())
#    except (SwitchException) as exc:
#        print(exc)
#        sw.remove_mgmt_interface(ifc)

    # Test add vlan to port
    print('Is vlan 16 "allowed" for port 18": ' + str(sw.is_vlan_allowed_for_port(16, 18)))

    exit(0)

    sw2 = SwitchFactory.factory(log, 'mellanox', '192.168.16.25', 'admin', 'admin')
    vlan_info = sw2.show_vlans()
    print(vlan_info)
    print(sw2.show_mac_address_table())

    sw3 = SwitchFactory.factory(log, 'mellanox', '192.168.16.30', 'admin', 'admin')
    print(sw3.show_vlans())
    print(sw3.show_mac_address_table())


if __name__ == '__main__':
    """Show status of the Cluster Genesis environment

    Args:
        INV_FILE (string): Inventory file.
        LOG_LEVEL (string): Log level.

    Raises:
       Exception: If parameter count is invalid.
    """

    LOG = Logger(__file__)
    ARGV_MAX = 3
    ARGV_COUNT = len(sys.argv)
    if ARGV_COUNT > ARGV_MAX:
        try:
            raise Exception()
        except:
            LOG.error('Invalid argument count')
            sys.exit(1)

    LOG.set_level('INFO')

    main(LOG)
