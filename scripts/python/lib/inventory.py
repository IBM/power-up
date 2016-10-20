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

import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader
from orderedattrdict import AttrDict

from lib.logger import Logger

CFG_IPADDR_MGMT_SWITCH = 'ipaddr-mgmt-switch'
CFG_IPADDR_DATA_SWITCH = 'ipaddr-data-switch'
CFG_HOSTNAME = 'hostname'
CFG_IPV4_ADDR = 'ipv4-addr'
CFG_USERID_DEFAULT = 'userid-default'
CFG_PASSWORD_DEFAULT = 'password-default'
CFG_USERID_MGMT_SWITCH = 'userid-mgmt-switch'
CFG_PASSWORD_MGMT_SWITCH = 'password-mgmt-switch'
CFG_USERID_DATA_SWITCH = 'userid-data-switch'
CFG_PASSWORD_DATA_SWITCH = 'password-data-switch'
CFG_RACK_ID = 'rack-id'
CFG_NODES_TEMPLATES = 'node-templates'
CFG_ETH_PORT = 'eth-port'
CFG_PORTS = 'ports'
CFG_ETH10 = 'eth10'
CFG_ETH11 = 'eth11'
CFG_IPMI_PORTS = 'ipmi-ports'
CFG_IPMI = 'ipmi'
CFG_PXE_PORTS = 'pxe-ports'
CFG_PXE = 'pxe'
CFG_ETH10_PORTS = 'eth10-ports'
CFG_ETH10 = 'eth10'
CFG_ETH11_PORTS = 'eth11-ports'
CFG_ETH11 = 'eth11'
CFG_USERID_IPMI = 'userid-ipmi'
CFG_PASSWORD_IPMI = 'password-ipmi'
CFG_NETWORKS = 'networks'
CFG_VLAN = 'vlan'
CFG_MTU = 'mtu'
CFG_MANAGEMENT_PORTS = ('ipmi', 'pxe')

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
INV_USERID_IPMI = 'userid-ipmi'
INV_PASSWORD_IPMI = 'password-ipmi'
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

    @staticmethod
    def _get_abs_path(file):
        return os.path.abspath(
            os.path.dirname(os.path.abspath(file)) +
            os.path.sep +
            os.path.basename(file))

    def __init__(self, log, inv_file, cfg_file=None):
        self.log = Logger(__file__)
        if cfg_file:
            self.cfg_file = self._get_abs_path(cfg_file)
            self.cfg = self.load(self.cfg_file)
        if inv_file:
            self.inv_file = self._get_abs_path(inv_file)
            if os.path.isfile(inv_file):
                self.inv = self.load(self.inv_file)

    def load(self, file):
        try:
            return yaml.load(open(file), Loader=AttrDictYAMLLoader)
        except:
            self.log.error('Could not load file: ' + file)
            sys.exit(1)

    def dump(self, inventory=None):
        if inventory is None:
            inventory = self.inv
        try:
            yaml.dump(
                inventory,
                open(self.inv_file, 'w'),
                indent=4,
                default_flow_style=False)
        except:
            self.log.error('Could not dump inventory to file: ' + self.inv_file)
            sys.exit(1)

    def add_switches(self):
        self.cfg = self.load(self.cfg_file)
        if (CFG_USERID_MGMT_SWITCH in self.cfg and
                self.cfg[CFG_USERID_MGMT_SWITCH] is not None):
                userid = self.cfg[CFG_USERID_MGMT_SWITCH]
        else:
            userid = self.cfg[CFG_USERID_DEFAULT]
        if (CFG_PASSWORD_MGMT_SWITCH in self.cfg and
                self.cfg[CFG_PASSWORD_MGMT_SWITCH] is not None):
                password = self.cfg[CFG_PASSWORD_MGMT_SWITCH]
        else:
            password = self.cfg[CFG_PASSWORD_DEFAULT]
        _list = []
        for index, (key, value) in enumerate(self.cfg[CFG_IPADDR_MGMT_SWITCH].items()):
            _dict = AttrDict()
            _dict[CFG_HOSTNAME] = INV_MGMTSWITCH + str(index+1)
            _dict[CFG_IPV4_ADDR] = value
            _dict[CFG_RACK_ID] = key
            _dict[INV_USERID] = userid
            _dict[INV_PASSWORD] = password
            _list.append(_dict)
        inv = AttrDict({})
        inv[INV_SWITCHES] = AttrDict({})
        inv[INV_SWITCHES][INV_MGMT] = _list

        if (CFG_USERID_DATA_SWITCH in self.cfg and
                self.cfg[CFG_USERID_DATA_SWITCH] is not None):
                userid = self.cfg[CFG_USERID_DATA_SWITCH]
        else:
            userid = self.cfg[CFG_USERID_DEFAULT]
        if (CFG_PASSWORD_DATA_SWITCH in self.cfg and
                self.cfg[CFG_PASSWORD_DATA_SWITCH] is not None):
                password = self.cfg[CFG_PASSWORD_DATA_SWITCH]
        else:
            password = self.cfg[CFG_PASSWORD_DEFAULT]
        _list = []
        for index, (key, value) in enumerate(self.cfg[CFG_IPADDR_DATA_SWITCH].items()):
            _dict = AttrDict()
            _dict[CFG_HOSTNAME] = INV_DATASWITCH + str(index+1)
            _dict[CFG_IPV4_ADDR] = value
            _dict[CFG_RACK_ID] = key
            _dict[INV_USERID] = userid
            _dict[INV_PASSWORD] = password
            _list.append(_dict)
        inv[INV_SWITCHES][INV_DATA] = _list

        self.dump(inv)

    def yield_data_vlans(self):
        _dict = AttrDict()
        __dict = AttrDict()
        _list = []
        userid = self.cfg[CFG_USERID_DATA_SWITCH]
        password = self.cfg[CFG_PASSWORD_DATA_SWITCH]
        for key, value in self.cfg[CFG_NODES_TEMPLATES].items():
            for _key, _value in value.items():
                if _key == CFG_PORTS:
                    for ports_key, ports_value in _value.items():
                        if ports_key != CFG_IPMI and ports_key != CFG_PXE:
                            for rack in ports_value:
                                for network in value[CFG_NETWORKS]:
                                    if CFG_VLAN in self.cfg[CFG_NETWORKS][network]:
                                        _dict[CFG_USERID_DATA_SWITCH] = userid
                                        _dict[CFG_PASSWORD_DATA_SWITCH] = password
                                        if self.cfg[CFG_NETWORKS][network][CFG_VLAN] not in _list:
                                            _list.append(self.cfg[CFG_NETWORKS][network][CFG_VLAN])
                                            _dict['vlan'] = _list
                                            __dict[self.cfg[CFG_IPADDR_DATA_SWITCH][rack]] = _dict
        for key, value in __dict.items():
            yield (
                key,
                value[CFG_USERID_DATA_SWITCH],
                value[CFG_PASSWORD_DATA_SWITCH],
                value['vlan'])

    def yield_data_switch_ports(self):
        _dict = AttrDict()
        __dict = AttrDict()
        ___dict = AttrDict()
        _dict['vlan'] = {}
        _dict['mtu'] = {}
        mtu = None
        userid = self.cfg[CFG_USERID_DATA_SWITCH]
        password = self.cfg[CFG_PASSWORD_DATA_SWITCH]
        for key, value in self.cfg[CFG_NODES_TEMPLATES].items():
            for _key, _value in value.items():
                if _key == CFG_PORTS:
                    for ports_key, ports_value in _value.items():
                        if ports_key != CFG_IPMI and ports_key != CFG_PXE:
                            for rack, ports in ports_value.items():
                                for port in ports:
                                    _list = []
                                    mtu = None
                                    for network in value[CFG_NETWORKS]:
                                        if CFG_ETH_PORT in self.cfg[CFG_NETWORKS][network].keys():
                                            if self.cfg[CFG_NETWORKS][network][CFG_ETH_PORT] == ports_key:
                                                if CFG_VLAN in self.cfg[CFG_NETWORKS][network]:
                                                    vlan = self.cfg[CFG_NETWORKS][network][CFG_VLAN]
                                                    _list.append(vlan)
                                                    _dict['vlan'][port] = _list
                                                if CFG_MTU in self.cfg[CFG_NETWORKS][network]:
                                                    if mtu is None:
                                                        mtu = self.cfg[CFG_NETWORKS][network][CFG_MTU]
                                                    else:
                                                        if mtu < self.cfg[CFG_NETWORKS][network][CFG_MTU]:
                                                            mtu = self.cfg[CFG_NETWORKS][network][CFG_MTU]
                                                    _dict['mtu'][port] = mtu
                                __dict[CFG_USERID_DATA_SWITCH] = userid
                                __dict[CFG_PASSWORD_DATA_SWITCH] = password
                                __dict['port_vlan'] = _dict['vlan']
                                __dict['port_mtu'] = _dict['mtu']
                                ___dict[self.cfg[CFG_IPADDR_DATA_SWITCH][rack]] = __dict
        for key, value in ___dict.items():
            yield (
                key,
                value[CFG_USERID_DATA_SWITCH],
                value[CFG_PASSWORD_DATA_SWITCH],
                value['port_vlan'],
                value['port_mtu'])

    def get_data_switches(self):
        # This methods a dict of switch IP to a dict with user
        # userid and password
        userid = self.cfg[CFG_USERID_DATA_SWITCH]
        password = self.cfg[CFG_PASSWORD_DATA_SWITCH]
        return_value = {}
        for rack_ip in self.cfg[CFG_IPADDR_DATA_SWITCH].values():
            return_value[rack_ip] = {'user': userid,
                                     'password': password}
        return return_value

    def yield_mgmt_rack_ipv4(self):
        self.cfg = self.load(self.cfg_file)
        for key, value in self.cfg[CFG_IPADDR_MGMT_SWITCH].items():
            yield key, value

    def create_nodes(self, dhcp_mac_ip, mgmt_switch_config):
        self.cfg = self.load(self.cfg_file)
        inv = self.inv
        inv[INV_NODES] = None
        _dict = AttrDict()
        for key, value in self.cfg[CFG_NODES_TEMPLATES].items():
            index = 0
            for rack, ipmi_ports in value[CFG_PORTS][CFG_IPMI].items():
                _list = []
                for port_index, ipmi_port in enumerate(ipmi_ports):
                    for mgmt_port in mgmt_switch_config[rack]:
                        if ipmi_port in mgmt_port.keys():
                            if mgmt_port[ipmi_port] in dhcp_mac_ip:
                                node_dict = AttrDict()
                                if (CFG_HOSTNAME not in value or
                                        value[CFG_HOSTNAME] is None):
                                    node_dict[INV_HOSTNAME] = key
                                else:
                                    node_dict[INV_HOSTNAME] = \
                                        value[CFG_HOSTNAME]
                                index += 1
                                node_dict[INV_HOSTNAME] += '-' + str(index)
                                node_dict[INV_USERID_IPMI] = \
                                    self.cfg[CFG_NODES_TEMPLATES][key][CFG_USERID_IPMI]
                                node_dict[INV_PASSWORD_IPMI] = \
                                    self.cfg[CFG_NODES_TEMPLATES][key][CFG_PASSWORD_IPMI]
                                node_dict[INV_PORT_IPMI] = ipmi_port
                                node_dict[INV_PORT_PXE] = \
                                    value[CFG_PORTS][CFG_PXE][rack][port_index]
                                node_dict[INV_PORT_ETH10] = \
                                    value[CFG_PORTS][CFG_ETH10][rack][port_index]
                                node_dict[INV_PORT_ETH11] = \
                                    value[CFG_PORTS][CFG_ETH11][rack][port_index]
                                node_dict[INV_MAC_IPMI] = mgmt_port[ipmi_port]
                                node_dict[INV_IPV4_IPMI] = \
                                    dhcp_mac_ip[mgmt_port[ipmi_port]]
                                node_dict[INV_RACK_ID] = rack
                                node_dict[INV_TEMPLATE] = key
                                _list.append(node_dict)
                                _dict[key] = _list
                                inv[INV_NODES] = _dict
        self.dump(inv)

    def add_pxe(self, dhcp_mac_ip, mgmt_switch_config):
        self.cfg = self.load(self.cfg_file)
        inv = self.inv
        _dict = AttrDict()
        for key, value in self.cfg[CFG_NODES_TEMPLATES].items():
            index = 0
            for rack, pxe_ports in value[CFG_PORTS][CFG_PXE].items():
                _list = []
                for port_index, pxe_port in enumerate(pxe_ports):
                    for mgmt_port in mgmt_switch_config[rack]:
                        if pxe_port in mgmt_port.keys():
                            if mgmt_port[pxe_port] in dhcp_mac_ip:
                                port = inv[INV_NODES][key][port_index][INV_PORT_PXE]
                                inv[INV_NODES][key][port_index][INV_MAC_PXE] = \
                                    mgmt_port[pxe_port]
                                inv[INV_NODES][key][port_index][INV_IPV4_PXE] = \
                                    dhcp_mac_ip[mgmt_port[pxe_port]]

        self.dump(inv)

    def yield_nodes(self):
        inv = self.inv
        for key, value in inv[INV_NODES].items():
            for index, node in enumerate(value):
                yield inv, INV_NODES, key, index, node

    def yield_node_ipmi(self):
        inv = self.inv
        for key, value in inv[INV_NODES].items():
            for node in value:
                yield (
                    node[INV_RACK_ID],
                    node[INV_MAC_IPMI],
                    node[INV_IPV4_IPMI])

    def yield_node_pxe(self):
        inv = self.inv
        for key, value in inv[INV_NODES].items():
            for node in value:
                yield (
                    node[INV_RACK_ID],
                    node[INV_MAC_PXE],
                    node[INV_IPV4_PXE])

    def yield_ipmi_access_info(self):
        inv = self.inv
        for key, value in inv[INV_NODES].items():
            for node in value:
                yield (
                    node[INV_RACK_ID],
                    node[INV_IPV4_IPMI],
                    node[INV_USERID_IPMI],
                    node[INV_PASSWORD_IPMI])

    def add_to_node(self, key, index, field, value):
        inv = self.inv
        inv[INV_NODES][key][index][field] = value
        self.dump(inv)

    def add_data_switch_port_macs(self, switch_to_port_to_macs):
        # Get map of rack IP to rack ID.
        ip_to_rack_id = {}
        for rack_id, rack_ip in self.inv[CFG_IPADDR_DATA_SWITCH].iteritems():
            ip_to_rack_id[rack_ip] = rack_id

        # Get list of all nodes
        nodes = [node for sublist in self.inv['nodes'].values() for node
                 in sublist]
        success = True
        for ip, switch_ports_to_MACs in switch_to_port_to_macs.iteritems():
            rack_id = ip_to_rack_id[ip]
            for node in nodes:
                if node['rack-id'] != rack_id:
                    continue
                node_template = self.inv[CFG_NODES_TEMPLATES][node[INV_TEMPLATE]]
                for port_name in node_template['ports'].keys():
                    if port_name not in CFG_MANAGEMENT_PORTS:
                        node_port_on_rack = str(node.get(INV_PORT_PATTERN % port_name, ''))
                        macs = switch_ports_to_MACs.get(node_port_on_rack, [])
                        if macs:
                            mac_key = INV_MAC_PATTERN % port_name
                            node[mac_key] = macs[0]
                        else:
                            msg = ('Unable to find a MAC address for %(port_name)s'
                                   ' of host %(host)s plugged into port %(node_port_on_rack)s'
                                   ' of switch %(switch)s')
                            msg_vars = {'port_name': port_name,
                                        'host': node.get(INV_IPV4_PXE),
                                        'node_port_on_rack': node_port_on_rack,
                                        'switch': ip}
                            print msg % msg_vars
                            success = False
        self.dump()
        return success
