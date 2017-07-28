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

import re
import readline
import yaml
import sys

from lib.logger import Logger
from lib.switch import SwitchFactory
from lib.switch_exception import SwitchException
from lib.switch_common import SwitchCommon
from lib.genesis import gen_passive_path, gen_path


def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()


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
    """Can be called from the command line with 0 arguments.

    Args:
        log:
        cfg: Dictionary of configuration values
    """
    _class = rlinput('\nEnter switch class: ', 'lenovo')
    cfg_file_path = gen_path + 'scripts/python/switch-test-cfg-{}.yml'
    try:
        cfg = yaml.load(open(cfg_file_path.format(_class)))
    except:
        print('Could not load file: ' + cfg_file_path.format(_class))
        print('Using default config file')
        try:
            cfg = yaml.load(open(cfg_file_path.format('')))
        except:
            print('Could not load file: ' + cfg_file_path.format(''))
            sys.xit(1)
    test = cfg['test']
    host = cfg['host']
    vlan = cfg['vlan']
    vlans = cfg['vlans']
    ifc_addr = cfg['ifc_addr']
    ifc_netmask = cfg['ifc_netmask']
    port = cfg['port']
    switchport_mode = cfg['switchport_mode']

    host = rlinput('Enter host address: ', host)
    cfg['host'] = host

    try:
        with open(__file__, 'r') as f:
            text = f.read()
    except IOError as error:
        print('Unable to open file {}'.format(__file__))
        print(error)
        sys.exit(0)
    sw = SwitchFactory.factory(log, _class, host, 'admin', 'admin', mode='active')
    test = 1

    while test != 0:
        _text = text
        print('\nAvailable tests')
        _text = _text.split('# Test')
        for line in _text:
            match = re.search(r'if (\d+) == test', line)
            if match:
                print(match.group(1) + ' - ' + line.splitlines()[0])
        test = int(rlinput('\nEnter a test to run: ', str(test)))
        cfg['test'] = test

        # Test Is switch pingable
        if 1 == test:
            print('\nTesting if switch is pingable')
            pingable = sw.is_pingable()
            if not pingable:
                print('Can not communicate with switch.  Exiting.')
            else:
                print('Switch {} is pingable: {} '.format(host, pingable))

        # Test create an in-band management interface
        if 2 == test:
            print('\nTesting in-band interface creation')
            vlan = int(rlinput('Enter interface vlan: ', str(vlan)))
            cfg['vlan'] = vlan
            ifc_addr = rlinput('Enter interface address: ', ifc_addr)
            cfg['ifc_addr'] = ifc_addr
            ifc_netmask = rlinput('Enter interface netmask: ', ifc_netmask)
            cfg['ifc_netmask'] = ifc_netmask
            try:
                sw.configure_interface(ifc_addr, ifc_netmask, vlan)
                print('Created interface vlan {}'.format(vlan))
            except SwitchException as exc:
                print (exc)

        # Test remove interface
        if 3 == test:
            print('Testing remove interface')
            vlan = int(rlinput('Enter interface vlan: ', str(vlan)))
            cfg['vlan'] = vlan
            ifc_addr = rlinput('Enter interface address: ', ifc_addr)
            cfg['ifc_addr'] = ifc_addr
            ifc_netmask = rlinput('Enter interface netmask: ', ifc_netmask)
            cfg['ifc_netmask'] = ifc_netmask
            try:
                sw.remove_interface(vlan, ifc_addr, ifc_netmask)
                print('Removed interface vlan {}'.format(vlan))
            except SwitchException as exc:
                print(exc)

        # Test show in-band interfaces
        if 4 == test:
            print('\nTesting show in-band interfaces')
            ifc = rlinput('Enter interface or vlan (leave blank to show all): ', '')
            format = rlinput('Enter format ("std" or leave blank ): ', 'std')
            if format == '':
                format = None
            ifcs = sw.show_interfaces(ifc, format=format)
            if format is None:
                print(ifcs)
            else:
                for ifc in ifcs:
                    print(ifc)

        # Test show mac address table
        if 5 == test:
            print('Test show mac address table: ')
            format = rlinput('Enter desired return format (std, dict or raw): ', 'std')
            macs = sw.show_mac_address_table(format=format)
            if format == 'raw':
                print(macs)
            elif format == 'dict' or format == 'std':
                print_dict(macs)

        # Test show vlans
        if 6 == test:
            print(sw.show_vlans())

        # Test create vlan
        if 7 == test:
            print('\nTest create vlan')
            vlan = int(rlinput('Enter vlan: ', str(vlan)))
            cfg['vlan'] = vlan
            try:
                sw.create_vlan(vlan)
                print('Created vlan {}'.format(vlan))
            except SwitchException as exc:
                print(exc)

        # Test delete vlan
        if 8 == test:
            print('\nTest deleting vlan')
            vlan = int(rlinput('Enter vlan: ', str(vlan)))
            cfg['vlan'] = vlan
            try:
                sw.delete_vlan(vlan)
                print('Deleted vlan {}'.format(vlan))
            except SwitchException as exc:
                print(exc)

        # Test is port in trunk mode
        if 9 == test:
            print('\nTesting is port in trunk mode')
            port = int(rlinput('Enter port #: ', str(port)))
            cfg['port'] = port
            print(sw.is_port_in_trunk_mode(port))

        # Test is port in access mode
        if 10 == test:
            print('\nTesting is port in access mode')
            port = int(rlinput('Enter port #: ', str(port)))
            cfg['port'] = port
            print(sw.is_port_in_access_mode(port))

        # Test set switchport mode
        if 11 == test:
            print('\nTesting set switchport mode')
            port = int(rlinput('Enter port #: ', str(port)))
            cfg['port'] = port
            vlan = rlinput('Enter vlan (blank for None): ', str(vlan))
            if vlan == '':
                vlan = None
            else:
                cfg['vlan'] = int(vlan)
            switchport_mode = rlinput('Enter switchport mode: ', switchport_mode)
            cfg['switchport_mode'] = switchport_mode
            try:
                sw.set_switchport_mode(switchport_mode, port, vlan)
                print('Set switchport mode to ' + switchport_mode)
            except SwitchException as exc:
                print(exc)

        # Test add vlans to port
        if 12 == test:
            print('\nTesting add vlans to port')
            port = int(rlinput('Enter port #: ', str(port)))
            cfg['port'] = port
            vlans = rlinput('Enter vlan list: ', vlans)
            cfg['vlans'] = vlans
            try:
                sw.add_vlans_to_port(port, vlans)
            except SwitchException as exc:
                print(exc)

        # Test remove vlans from port
        if 13 == test:
            print('\nTesting remove vlans from port')
            port = int(rlinput('Enter port #: ', str(port)))
            cfg['port'] = port
            vlans = rlinput('Enter vlan list: ', vlans)
            cfg['vlans'] = vlans
            try:
                sw.remove_vlans_from_port(port, vlans)
            except SwitchException as exc:
                print(exc)

        # Test is vlan allowed for port
        if 14 == test:
            print('\nTesting is vlan allowed for port')
            port = int(rlinput('Enter port #: ', str(port)))
            cfg['port'] = port
            vlan = int(rlinput('Enter vlan: ', str(vlan)))
            cfg['vlan'] = vlan
            print(sw.is_vlan_allowed_for_port(vlan, port))

        # Test show ports
        if 15 == test:
            print('\nTesting show ports')
            format = rlinput('Enter format ("std" or leave blank ): ', 'std')
            if format == '':
                format = None
            ports = sw.show_ports(format=format)
            if format is None:
                print(ports)
            else:
                print_dict(ports)

        # Test show native vlan
        if 16 == test:
            print('\nTesting show native vlan')
            port = int(rlinput('Enter port #: ', str(port)))
            cfg['port'] = port
            print('Native vlan: {}'.format(sw.show_native_vlan(port)))

        # Test set native vlan
        if 17 == test:
            print('\nSet native vlan')
            port = int(rlinput('Enter port #: ', str(port)))
            cfg['port'] = port
            vlan = rlinput('Enter vlan #: ', vlan)
            cfg['vlan'] = vlan
            try:
                sw.set_switchport_native_vlan(vlan, port)
                print('Set native vlan succesful')
            except SwitchException as exc:
                print(exc)

        yaml.dump(cfg, open(cfg_file_path.format(_class), 'w'), default_flow_style=False)
        _ = rlinput('\nPress enter to continue, 0 to end ', '')
        if _ == '0':
            test = 0
    sys.exit(0)

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
    ifc_info = sw.show_interfaces()
    print(ifc_info)

#    if '55: ' in ifc_info:
#        print('Interface 55 already in use')
#        sys.exit(1)
#    print('Configure mgmt interface 55: ')
#    try:
#        sw.configure_interface('192.168.17.17', '255.255.255.0', vlan=17, intf=55)
#        print(sw.show_interfaces())
#        sw.remove_interface(55)
#    except (SwitchException) as exc:
#        print(exc)
#
#    # test configure next available interface
#    print('Finding next available interface')
#    ifc_info = sw.show_interfaces()
#    ifc = _get_available_interface(ifc_info)
#    print('Next available interface %d' % ifc)
#    try:
#        sw.configure_interface('192.168.18.18', '255.255.255.0', vlan=18)
#        print(sw.show_interfaces())
#        sw.remove_interface(ifc)
#        print(sw.show_interfaces())
#    except (SwitchException) as exc:
#        print(exc)
#        sw.remove_interface(ifc)

    # Test add vlan to port
    print('Is vlan 16 "allowed" for port 18": ' + str(sw.is_vlan_allowed_for_port(16, 18)))

    sys.exit(0)

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
        tests (string): string of tests to run. ex 245 will run tests 2,4
        and 5.  99 will run all tests.
        _class (string): switch class.  ie lenovo
        host (string): switch address. ie 192.168.32.20

    Raises:
       Exception: If parameter count is invalid.
    """

    LOG = Logger(__file__)
    LOG.set_level('INFO')
    main(LOG)
