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

import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
from orderedattrdict import AttrDict

from lib.logger import Logger

INV_IPADDR_MGMT_NETWORK = 'ipaddr-mgmt-network'
INV_IPADDR_MGMT_SWITCH = 'ipaddr-mgmt-switch'
INV_LABEL_MGMT_SWITCH_EXTERNAL_DEV = 'label-mgmt-switch-external-dev'
INV_CIDR_MGMT_SWITCH_EXTERNAL_DEV = 'cidr-mgmt-switch-external-dev'
INV_IPADDR_MGMT_SWITCH_EXTERNAL = 'ipaddr-mgmt-switch-external'
INV_IPADDR_DATA_SWITCH = 'ipaddr-data-switch'
INV_IPADDR_MLAG_VIP = 'ipaddr-mlag-vip'
INV_CIDR_MLAG_IPL = 'cidr-mlag-ipl'
INV_MLAG_VLAN = 'mlag-vlan'
INV_MLAG_PORT_CHANNEL = 'mlag-port-channel'
INV_MLAG_IPL_PORTS = 'mlag-ipl-ports'
INV_IPV4_ADDR = 'ipv4-addr'
INV_USERID_DEFAULT = 'userid-default'
INV_PASSWORD_DEFAULT = 'password-default'
INV_USERID_MGMT_SWITCH = 'userid-mgmt-switch'
INV_PASSWORD_MGMT_SWITCH = 'password-mgmt-switch'
INV_USERID_DATA_SWITCH = 'userid-data-switch'
INV_PASSWORD_DATA_SWITCH = 'password-data-switch'
INV_NODES_TEMPLATES = 'node-templates'
INV_ETH_PORT = 'eth-port'
INV_BOND_INTS = 'bond-interfaces'
INV_BOND = 'bond'
INV_BOND_PRIMARY = 'bond-primary'
INV_PORTS = 'ports'
INV_ETH10 = 'eth10'
INV_ETH11 = 'eth11'
INV_ETH12 = 'eth12'
INV_ETH13 = 'eth13'
INV_IPMI = 'ipmi'
INV_PXE = 'pxe'
INV_USERID_IPMI = 'userid-ipmi'
INV_PASSWORD_IPMI = 'password-ipmi'
INV_NETWORKS = 'networks'
INV_VLAN_MGMT_NETWORK = 'vlan-mgmt-network'
INV_VLAN_MGMT_CLIENT_NETWORK = 'vlan-mgmt-client-network'
INV_PORT_MGMT_NETWORK = 'port-mgmt-network'
INV_PORT_MGMT_DATA_NETWORK = 'port-mgmt-data-network'
INV_VLAN = 'vlan'
INV_MTU = 'mtu'
INV_MANAGEMENT_PORTS = ('ipmi', 'pxe')
INV_SWITCHES = 'switches'
INV_MGMT = 'mgmt'
INV_DATA = 'data'
INV_MGMTSWITCH = 'mgmtswitch'
INV_DATASWITCH = 'dataswitch'
INV_USERID = 'userid'
INV_PASSWORD = 'password'
INV_NODES = 'nodes'
INV_HOSTNAME = 'hostname'
INV_PORT_PATTERN = 'port-%s'
INV_PORT_IPMI = 'port-ipmi'
INV_PORT_PXE = 'port-pxe'
INV_IPV4_IPMI = 'ipv4-ipmi'
INV_IPV4_PXE = 'ipv4-pxe'
INV_MAC_PATTERN = 'mac-%s'
INV_MAC_IPMI = 'mac-ipmi'
INV_MAC_PXE = 'mac-pxe'
INV_RACK_ID = 'rack-id'
INV_PORT_ETH10 = 'port-eth10'
INV_PORT_ETH11 = 'port-eth11'
INV_PORT_ETH12 = 'port-eth12'
INV_PORT_ETH13 = 'port-eth13'
INV_OS_DISK = 'os-disk'
INV_TEMPLATE = 'template'


class Inventory():
    INV_CHASSIS_PART_NUMBER = 'chassis-part-number'
    INV_CHASSIS_SERIAL_NUMBER = 'chassis-serial-number'
    INV_MODEL = 'model'
    INV_SERIAL_NUMBER = 'serial-number'
    INV_IPV4_IPMI = 'ipv4-ipmi'
    INV_USERID_IPMI = 'userid-ipmi'
    INV_PASSWORD_IPMI = 'password-ipmi'
    INV_ARCHITECTURE = 'architecture'

    def __init__(self, log, inv_file):
        self.log = Logger(__file__)
        self.inv_file = os.path.abspath(
            os.path.dirname(os.path.abspath(inv_file)) +
            os.path.sep +
            os.path.basename(inv_file))
        self.inv = self._load_inv_file()

    def _load_inv_file(self):
        try:
            return yaml.load(open(self.inv_file), Loader=AttrDictYAMLLoader)
        except:
            self.log.error('Could not load file: ' + self.inv_file)
            sys.exit(1)

    def _dump_inv_file(self):
        try:
            yaml.dump(
                self.inv,
                open(self.inv_file, 'w'),
                indent=4,
                default_flow_style=False)
        except:
            self.log.error(
                'Could not dump inventory to file: ' + self.inv_file)
            sys.exit(1)

    def get_ipaddr_mgmt_network(self):
        return self.inv[INV_IPADDR_MGMT_NETWORK]

    def add_switches(self):
        if (INV_USERID_MGMT_SWITCH in self.inv and
                self.inv[INV_USERID_MGMT_SWITCH] is not None):
                userid = self.inv[INV_USERID_MGMT_SWITCH]
        else:
            userid = self.inv[INV_USERID_DEFAULT]
        if (INV_PASSWORD_MGMT_SWITCH in self.inv and
                self.inv[INV_PASSWORD_MGMT_SWITCH] is not None):
                password = self.inv[INV_PASSWORD_MGMT_SWITCH]
        else:
            password = self.inv[INV_PASSWORD_DEFAULT]
        _list = []
        for index, (key, value) in (
                enumerate(self.inv[INV_IPADDR_MGMT_SWITCH].items())):
            _dict = AttrDict()
            _dict[INV_HOSTNAME] = INV_MGMTSWITCH + str(index + 1)
            _dict[INV_IPV4_ADDR] = value
            _dict[INV_RACK_ID] = key
            _dict[INV_USERID] = userid
            _dict[INV_PASSWORD] = password
            _list.append(_dict)
        inv = AttrDict({})
        inv[INV_SWITCHES] = AttrDict({})
        inv[INV_SWITCHES][INV_MGMT] = _list

        if (INV_USERID_DATA_SWITCH in self.inv and
                self.inv[INV_USERID_DATA_SWITCH] is not None):
                userid = self.inv[INV_USERID_DATA_SWITCH]
        else:
            userid = self.inv[INV_USERID_DEFAULT]
        if (INV_PASSWORD_DATA_SWITCH in self.inv and
                self.inv[INV_PASSWORD_DATA_SWITCH] is not None):
                password = self.inv[INV_PASSWORD_DATA_SWITCH]
        else:
            password = self.inv[INV_PASSWORD_DEFAULT]
        _list = []
        for index, (key, value) in (
                enumerate(self.inv[INV_IPADDR_DATA_SWITCH].items())):
            _dict = AttrDict()
            _dict[INV_HOSTNAME] = INV_DATASWITCH + str(index + 1)
            if value == list:
                _dict[INV_IPV4_ADDR] = value.copy()
            else:
                _dict[INV_IPV4_ADDR] = value
            _dict[INV_RACK_ID] = key
            _dict[INV_USERID] = userid
            _dict[INV_PASSWORD] = password
            _list.append(_dict)
        inv[INV_SWITCHES][INV_DATA] = _list

        self.inv[INV_SWITCHES] = inv
        self._dump_inv_file()

    def yield_mgmt_switch_ip(self):
        for ipv4 in self.inv[INV_IPADDR_MGMT_SWITCH].values():
            yield ipv4

    def get_vlan_mgmt_network(self):
        return self.inv[INV_VLAN_MGMT_NETWORK]

    def get_vlan_mgmt_client_network(self):
        return self.inv[INV_VLAN_MGMT_CLIENT_NETWORK]

    def get_port_mgmt_network(self):
        return self.inv[INV_PORT_MGMT_NETWORK]

    def yield_ports_mgmt_data_network(self):
        for ports in self.inv[INV_PORT_MGMT_DATA_NETWORK].values():
            if type(ports) is list:
                for port in ports:
                    yield port
            else:
                yield ports

    def get_userid_mgmt_switch(self):
        return self.inv[INV_USERID_MGMT_SWITCH]

    def get_password_mgmt_switch(self):
        return self.inv[INV_PASSWORD_MGMT_SWITCH]

    def yield_mgmt_switch_ports(self):
        port_list = []
        for key, value in self.inv[INV_NODES_TEMPLATES].items():
            for _key, _value in value.items():
                if _key == INV_PORTS:
                    for ports_key, ports_value in _value.items():
                        if ports_key == INV_IPMI or ports_key == INV_PXE:
                            for rack, ports in ports_value.items():
                                for port in ports:
                                    port_list.append(port)
        for port in port_list:
            yield port

    def get_mgmt_switch_external_dev_label(self):
        if INV_LABEL_MGMT_SWITCH_EXTERNAL_DEV in self.inv:
            return self.inv[INV_LABEL_MGMT_SWITCH_EXTERNAL_DEV]

    def get_mgmt_switch_external_dev_ip(self):
        return self.inv[INV_CIDR_MGMT_SWITCH_EXTERNAL_DEV].split('/')[0]

    def get_mgmt_switch_external_prefix(self):
        return self.inv[INV_CIDR_MGMT_SWITCH_EXTERNAL_DEV].split('/')[1]

    def yield_mgmt_switch_external_switch_ip(self):
        for ipv4 in self.inv[INV_IPADDR_MGMT_SWITCH_EXTERNAL].values():
            yield ipv4

    def yield_data_vlans(self):
        _dict = AttrDict()
        __dict = AttrDict()
        vlan_list = []
        vlan_dict = AttrDict()
        userid = self.inv[INV_USERID_DATA_SWITCH]
        password = self.inv[INV_PASSWORD_DATA_SWITCH]
        for key, value in self.inv[INV_NODES_TEMPLATES].items():
            for _key, _value in value.items():
                if _key == INV_PORTS:
                    switch_index = 0
                    for ports_key, ports_value in _value.items():
                        if ports_key != INV_IPMI and ports_key != INV_PXE:
                            for rack in ports_value:
                                if switch_index not in vlan_dict:
                                    vlan_dict[switch_index] = []
                                for network in value[INV_NETWORKS]:
                                    if INV_VLAN in self.inv[INV_NETWORKS][network]:
                                        _dict[INV_USERID_DATA_SWITCH] = userid
                                        _dict[INV_PASSWORD_DATA_SWITCH] = password
                                        if (type(self.inv[INV_IPADDR_DATA_SWITCH][rack]) == list and
                                                len(self.inv[INV_IPADDR_DATA_SWITCH][rack]) == 2):
                                            if self.inv[INV_NETWORKS][network][INV_VLAN] not in vlan_dict[switch_index]:
                                                vlan_dict[switch_index].append(self.inv[INV_NETWORKS][network][INV_VLAN])
                                                _dict['vlan'] = vlan_dict[switch_index]
                                                __dict[self.inv[INV_IPADDR_DATA_SWITCH][rack][switch_index]] = _dict
                                        else:
                                            if self.inv[INV_NETWORKS][network][INV_VLAN] not in vlan_list:
                                                vlan_list.append(self.inv[INV_NETWORKS][network][INV_VLAN])
                                                _dict['vlan'] = vlan_list
                                                if type(self.inv[INV_IPADDR_DATA_SWITCH][rack]) == list:
                                                    __dict[self.inv[INV_IPADDR_DATA_SWITCH][rack][0]] = _dict
                                                else:
                                                    __dict[self.inv[INV_IPADDR_DATA_SWITCH][rack]] = _dict
                            switch_index += 1
        for key, value in __dict.items():
            yield (
                key,
                value[INV_USERID_DATA_SWITCH],
                value[INV_PASSWORD_DATA_SWITCH],
                value['vlan'])

    def yield_data_switch_ports(self):
        _dict = AttrDict()
        __dict = AttrDict()
        ___dict = AttrDict()
        _dict['vlan'] = AttrDict()
        _dict['mtu'] = AttrDict()
        _dict['bonds'] = AttrDict()
        mtu = None
        userid = self.inv[INV_USERID_DATA_SWITCH]
        password = self.inv[INV_PASSWORD_DATA_SWITCH]
        for key, value in self.inv[INV_NODES_TEMPLATES].items():
            for _key, _value in value.items():
                if _key == INV_PORTS:
                    switch_index = 0
                    for ports_key, ports_value in _value.items():
                        if ports_key != INV_IPMI and ports_key != INV_PXE:
                            for rack, ports in ports_value.items():
                                port_index = 0
                                for port in ports:
                                    _list = []
                                    mtu = None
                                    for network in value[INV_NETWORKS]:
                                        if INV_ETH_PORT in self.inv[INV_NETWORKS][network].keys():
                                            if self.inv[INV_NETWORKS][network][INV_ETH_PORT] == ports_key:
                                                if INV_VLAN in self.inv[INV_NETWORKS][network]:
                                                    vlan = self.inv[INV_NETWORKS][network][INV_VLAN]
                                                    _list.append(vlan)
                                                    _dict['vlan'][port] = _list
                                                if INV_MTU in self.inv[INV_NETWORKS][network]:
                                                    if mtu is None:
                                                        mtu = self.inv[INV_NETWORKS][network][INV_MTU]
                                                    else:
                                                        if mtu < self.inv[INV_NETWORKS][network][INV_MTU]:
                                                            mtu = self.inv[INV_NETWORKS][network][INV_MTU]
                                                    _dict['mtu'][port] = mtu
                                        elif INV_BOND_INTS in self.inv[INV_NETWORKS][network].keys():
                                            bond_interfaces = self.inv[INV_NETWORKS][network][INV_BOND_INTS]
                                            bond_name = self.inv[INV_NETWORKS][network][INV_BOND]
                                            if ports_key in bond_interfaces:
                                                if INV_BOND_PRIMARY in self.inv[INV_NETWORKS][network].keys():
                                                    if self.inv[INV_NETWORKS][network][INV_BOND_PRIMARY] == ports_key:
                                                        _dict['bonds'][port] = []
                                                        for int_port in bond_interfaces:
                                                            _dict['bonds'][port].append(_value[int_port][rack][port_index])
                                                elif bond_interfaces[0] == ports_key:
                                                    _dict['bonds'][port] = []
                                                    for int_port in bond_interfaces:
                                                        _dict['bonds'][port].append(_value[int_port][rack][port_index])
                                                if INV_VLAN in self.inv[INV_NETWORKS][network]:
                                                    vlan = self.inv[INV_NETWORKS][network][INV_VLAN]
                                                    _list.append(vlan)
                                                    _dict['vlan'][port] = _list
                                                if INV_MTU in self.inv[INV_NETWORKS][network]:
                                                    if mtu is None:
                                                        mtu = self.inv[INV_NETWORKS][network][INV_MTU]
                                                    else:
                                                        if mtu < self.inv[INV_NETWORKS][network][INV_MTU]:
                                                            mtu = self.inv[INV_NETWORKS][network][INV_MTU]
                                                    _dict['mtu'][port] = mtu
                                                for network in value[INV_NETWORKS]:
                                                    if INV_ETH_PORT in self.inv[INV_NETWORKS][network].keys():
                                                        if self.inv[INV_NETWORKS][network][INV_ETH_PORT] == bond_name:
                                                            if INV_VLAN in self.inv[INV_NETWORKS][network]:
                                                                vlan = self.inv[INV_NETWORKS][network][INV_VLAN]
                                                                _list.append(vlan)
                                                                _dict['vlan'][port] = _list
                                                            if INV_MTU in self.inv[INV_NETWORKS][network]:
                                                                if mtu is None:
                                                                    mtu = self.inv[INV_NETWORKS][network][INV_MTU]
                                                                else:
                                                                    if mtu < self.inv[INV_NETWORKS][network][INV_MTU]:
                                                                        mtu = self.inv[INV_NETWORKS][network][INV_MTU]
                                                                _dict['mtu'][port] = mtu
                                    port_index += 1
                                __dict[INV_USERID_DATA_SWITCH] = userid
                                __dict[INV_PASSWORD_DATA_SWITCH] = password
                                __dict['port_vlan'] = _dict['vlan']
                                __dict['port_mtu'] = _dict['mtu']
                                __dict['port_bonds'] = _dict['bonds']
                                if (type(self.inv[INV_IPADDR_DATA_SWITCH][rack]) == list and
                                        len(self.inv[INV_IPADDR_DATA_SWITCH][rack]) == 2):
                                    ___dict[self.inv[INV_IPADDR_DATA_SWITCH][rack][switch_index]] = __dict.copy()
                                else:
                                    if type(self.inv[INV_IPADDR_DATA_SWITCH][rack]) == list:
                                        ___dict[self.inv[INV_IPADDR_DATA_SWITCH][rack][0]] = __dict
                                    else:
                                        ___dict[self.inv[INV_IPADDR_DATA_SWITCH][rack]] = __dict
                            switch_index += 1
        for key, value in ___dict.items():
            yield (
                key,
                value[INV_USERID_DATA_SWITCH],
                value[INV_PASSWORD_DATA_SWITCH],
                value['port_vlan'],
                value['port_mtu'],
                value['port_bonds'])

    def is_mlag(self):
        for value in self.inv[INV_IPADDR_DATA_SWITCH].values():
            if type(value) == list and len(value) == 2:
                return True
        return False

    def get_mlag_vlan(self):
        for value in self.inv[INV_MLAG_VLAN].values():
            pass
        return value

    def get_mlag_port_channel(self):
        for value in self.inv[INV_MLAG_PORT_CHANNEL].values():
            pass
        return value

    def get_cidr_mlag_ipl(self, switch_index):
        for value in self.inv[INV_CIDR_MLAG_IPL].values():
            pass
        return value[switch_index].replace('/', ' /')

    def get_ipaddr_mlag_ipl_peer(self, switch_index):
        for value in self.inv[INV_CIDR_MLAG_IPL].values():
            pass
        if switch_index:
            index = 0
        else:
            index = 1
        return value[index].split('/')[0]

    def get_ipaddr_mlag_vip(self):
        for value in self.inv[INV_IPADDR_MLAG_VIP].values():
            pass
        return (
            value +
            ' /' +
            self.inv[INV_IPADDR_MGMT_NETWORK].split('/')[1])

    def yield_mlag_ports(self, switch_index):
        for value in self.inv[INV_MLAG_IPL_PORTS].values():
            for port in value[switch_index]:
                yield port

    def get_data_switches(self):
        # This methods a dict of switch IP to a dict with user
        # userid and password
        userid = self.inv[INV_USERID_DATA_SWITCH]
        password = self.inv[INV_PASSWORD_DATA_SWITCH]
        return_value = AttrDict()
        for rack_ip in self.inv[INV_IPADDR_DATA_SWITCH].values():
            if type(rack_ip) == list:
                for ip in rack_ip:
                    return_value[ip] = {
                        'user': userid,
                        'password': password}
            else:
                return_value[rack_ip] = {
                    'user': userid,
                    'password': password}
        return return_value

    def yield_mgmt_rack_ipv4(self):
        for key, value in self.inv[INV_IPADDR_MGMT_SWITCH].items():
            yield key, value

    def create_nodes(self, dhcp_mac_ip, mgmt_switch_config):
        if INV_NODES in self.inv:
            _dict = self.inv[INV_NODES]
        else:
            self.inv[INV_NODES] = None
            _dict = AttrDict()
        for key, value in self.inv[INV_NODES_TEMPLATES].items():
            index = 0
            for rack, ipmi_ports in value[INV_PORTS][INV_IPMI].items():
                _list = []
                for port_index, ipmi_port in enumerate(ipmi_ports):
                    for mgmt_port in mgmt_switch_config[rack]:
                        if ipmi_port in mgmt_port.keys():
                            if mgmt_port[ipmi_port] in dhcp_mac_ip:
                                node_dict = AttrDict()
                                if (INV_HOSTNAME not in value or
                                        value[INV_HOSTNAME] is None):
                                    node_dict[INV_HOSTNAME] = key
                                else:
                                    node_dict[INV_HOSTNAME] = \
                                        value[INV_HOSTNAME]
                                index += 1
                                node_dict[INV_HOSTNAME] += '-' + str(index)
                                node_dict[INV_USERID_IPMI] = \
                                    self.inv[INV_NODES_TEMPLATES][key][INV_USERID_IPMI]
                                node_dict[INV_PASSWORD_IPMI] = \
                                    self.inv[INV_NODES_TEMPLATES][key][INV_PASSWORD_IPMI]
                                node_dict[INV_PORT_IPMI] = ipmi_port
                                node_dict[INV_PORT_PXE] = \
                                    value[INV_PORTS][INV_PXE][rack][port_index]
                                if INV_ETH10 in value[INV_PORTS]:
                                    node_dict[INV_PORT_ETH10] = \
                                        value[INV_PORTS][INV_ETH10][rack][port_index]
                                if INV_ETH11 in value[INV_PORTS]:
                                    node_dict[INV_PORT_ETH11] = \
                                        value[INV_PORTS][INV_ETH11][rack][port_index]
                                if INV_ETH12 in value[INV_PORTS]:
                                    node_dict[INV_PORT_ETH12] = \
                                        value[INV_PORTS][INV_ETH12][rack][port_index]
                                if INV_ETH13 in value[INV_PORTS]:
                                    node_dict[INV_PORT_ETH13] = \
                                        value[INV_PORTS][INV_ETH13][rack][port_index]
                                node_dict[INV_MAC_IPMI] = mgmt_port[ipmi_port]
                                node_dict[INV_IPV4_IPMI] = \
                                    dhcp_mac_ip[mgmt_port[ipmi_port]]
                                node_dict[INV_RACK_ID] = rack
                                node_dict[INV_TEMPLATE] = key
                                if INV_OS_DISK in value:
                                    node_dict[INV_OS_DISK] = value[INV_OS_DISK]
                                _list.append(node_dict)
                                _dict[key] = _list
                                self.inv[INV_NODES] = _dict
        if self.inv[INV_NODES] is not None:
            self._dump_inv_file()

    def add_pxe(self, dhcp_mac_ip, mgmt_switch_config):
        for key, value in self.inv[INV_NODES_TEMPLATES].items():
            for rack, pxe_ports in value[INV_PORTS][INV_PXE].items():
                for port_index, pxe_port in enumerate(pxe_ports):
                    for mgmt_port in mgmt_switch_config[rack]:
                        if pxe_port in mgmt_port.keys():
                            if mgmt_port[pxe_port] in dhcp_mac_ip:
                                self.inv[INV_NODES][key][port_index][INV_MAC_PXE] = \
                                    mgmt_port[pxe_port]
                                self.inv[INV_NODES][key][port_index][INV_IPV4_PXE] = \
                                    dhcp_mac_ip[mgmt_port[pxe_port]]

        self._dump_inv_file()

    def yield_nodes(self):
        for key, value in self.inv[INV_NODES].items():
            for index, node in enumerate(value):
                yield self.inv, INV_NODES, key, index, node

    def get_node_count(self):
        count = 0
        for key, value in self.inv[INV_NODES].items():
            for index, node in enumerate(value):
                count += 1
        return count

    def yield_node_ipmi(self):
        for key, value in self.inv[INV_NODES].items():
            for node in value:
                yield (
                    node[INV_RACK_ID],
                    node[INV_MAC_IPMI],
                    node[INV_IPV4_IPMI])

    def yield_node_pxe(self):
        for key, value in self.inv[INV_NODES].items():
            for node in value:
                yield (
                    node[INV_RACK_ID],
                    node[INV_MAC_PXE],
                    node[INV_IPV4_PXE])

    def yield_ipmi_access_info(self):
        for key, value in self.inv[INV_NODES].items():
            for node in value:
                yield (
                    node[INV_RACK_ID],
                    node[INV_IPV4_IPMI],
                    node[INV_USERID_IPMI],
                    node[INV_PASSWORD_IPMI])

    def yield_template_ports(self, port_type):
        for template, value in self.inv[INV_NODES_TEMPLATES].items():
            if port_type in value[INV_PORTS]:
                for rack, ports in value[INV_PORTS][port_type].items():
                    yield (template, rack, ports)

    def check_port(self, template, port_type, rack, port):
        # Find node associated with given port number and if both mac-* and
        # ipv4-* keys defined return tuple
        if self.inv[INV_NODES] is not None:
            for key, value in self.inv[INV_NODES].items():
                for node in value:
                    if node['port-' + port_type] == port:
                        if (('mac-' + port_type) in node and
                                ('ipv4-' + port_type) in node):
                            return (node['mac-' + port_type],
                                    node['ipv4-' + port_type])
        return False

    def add_to_node(self, key, index, field, value):
        self.inv[INV_NODES][key][index][field] = value
        self._dump_inv_file()

    def add_data_switch_port_macs(self, switch_to_port_to_macs):
        # Get map of rack IP to rack ID.
        ip_to_rack_id = {}
        for rack_id, rack_ip in self.inv[INV_IPADDR_DATA_SWITCH].iteritems():
            if type(rack_ip) == list:
                for ip in rack_ip:
                    ip_to_rack_id[ip] = rack_id
            else:
                ip_to_rack_id[rack_ip] = rack_id

        # Get list of all nodes
        nodes = [node for sublist in self.inv['nodes'].values() for node
                 in sublist]
        success = True
        index = 0
        for ip, switch_ports_to_MACs in switch_to_port_to_macs.iteritems():
            rack_id = ip_to_rack_id[ip]
            for node in nodes:
                if node['rack-id'] != rack_id:
                    continue
                node_template = self.inv[INV_NODES_TEMPLATES][node[INV_TEMPLATE]]
                for port_name in node_template['ports'].keys():
                    if port_name not in INV_MANAGEMENT_PORTS:
                        if (not self.is_mlag() or
                                (self.is_mlag() and index == 0 and port_name == INV_ETH10) or
                                (self.is_mlag() and index == 1 and port_name == INV_ETH11) or
                                (self.is_mlag() and index == 0 and port_name == INV_ETH12) or
                                (self.is_mlag() and index == 1 and port_name == INV_ETH13)):
                            node_port_on_rack = str(node.get(INV_PORT_PATTERN %
                                                    port_name, ''))
                            macs = switch_ports_to_MACs.get(node_port_on_rack, [])
                            if macs:
                                mac_key = INV_MAC_PATTERN % port_name
                                node[mac_key] = macs[0]
                            else:
                                msg = ('Unable to find a MAC address for '
                                       '%(port_name)s of host %(host)s plugged '
                                       'into port %(node_port_on_rack)s of switch '
                                       '%(switch)s')
                                msg_vars = {'port_name': port_name,
                                            'host': node.get(INV_IPV4_PXE),
                                            'node_port_on_rack': node_port_on_rack,
                                            'switch': ip}
                                print msg % msg_vars
                                success = False
            index += 1
        self._dump_inv_file()
        return success
