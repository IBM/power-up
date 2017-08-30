"""Config"""

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
from enum import Enum
import logging
import netaddr

from lib.logger import Logger
from lib.db import Database


class Config(object):
    """Config
    """

    class SwitchType(Enum):
        MGMT, DATA = range(2)

    class CfgKey(object):
        LABEL = 'label'
        HOSTNAME = 'hostname'
        USERID = 'userid'
        PASSWORD = 'password'
        SSH_KEY = 'ssh_key'
        ROOM = 'room'
        ROW = 'row'
        CELL = 'cell'
        IPADDR = 'ipaddr'
        PORT = 'port'
        TYPE = 'type'
        SWITCH = 'switch'
        RACK_ID = 'rack_id'
        RACK_EIA = 'rack_eia'
        HOSTNAME_PREFIX = 'hostname_prefix'
        DEVICE = 'device'
        INTERFACE_IPADDR = 'interface_ipaddr'
        CONTAINER_IPADDR = 'container_ipaddr'
        BRIDGE_IPADDR = 'bridge_ipaddr'
        VLAN = 'vlan'
        NETMASK = 'netmask'
        PREFIX = 'prefix'

    def __init__(self):
        self.log = logging.getLogger(Logger.LOG_NAME)
        dbase = Database()
        self.cfg = dbase.load_config()

    @staticmethod
    def _netmask_to_prefix(netmask):
        """Convert Netmask to Prefix
        Args:
            netmask (str): Netmask

        Returns:
            int: Prefix
        """

        return netaddr.IPAddress(netmask).netmask_bits()

    @staticmethod
    def _prefix_to_netmask(prefix):
        """Convert Prefix to Netmask
        Args:
            prefix (int): Prefix

        Returns:
            str: Netmask
        """

        return str(netaddr.IPNetwork('255.255.255.255/' + str(prefix)).netmask)

    def _netmask_prefix_not_found(self):
        """Check if Netmask or Prefix is specified
        Raises:
            Exception: If neither Netmask nor Prefix is specified
        """
        try:
            raise Exception()
        except Exception:
            self.log.error("Neither 'netmask' nor 'prefix' is specified")
            sys.exit(1)

    @staticmethod
    def _get_members(obj_list, key, index):
        """Get dictionary value under a list
        Args:
            obj_list (list): Object list
            key (dict key): Dictionary key
            index (int): Index

        Returns:
            list or obj: Members or member
        """

        if index is None:
            list_ = []
            for member in obj_list:
                if key in member:
                    list_.append(getattr(member, key))
                else:
                    list_.append(None)
            return list_
        if key in obj_list[index]:
            return getattr(obj_list[index], key)

    def get_version(self):
        """Get version
        Returns:
            str: Config file version
        """

        return self.cfg.version

    def get_globals_log_level(self):
        """Get globals log_level
        Returns:
            str: Log level
        """

        return self.cfg.globals.log_level

    def get_loc_time_zone(self):
        """Get location time_zone
        Returns:
            str: Time zone
        """

        return self.cfg.location.time_zone

    def get_loc_data_center(self):
        """Get location data_center
        Returns:
            str: Data center
        """

        return self.cfg.location.data_center

    def get_loc_racks_cnt(self):
        """Get location racks count
        Returns:
            int: Racks count
        """

        return len(self.cfg.location.racks)

    def get_loc_racks_label(self, index=None):
        """Get location racks label
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Label member or list
        """

        return self._get_members(
            self.cfg.location.racks, self.CfgKey.LABEL, index)

    def get_loc_racks_room(self, index=None):
        """Get location racks room
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Room member or list
        """

        return self._get_members(
            self.cfg.location.racks, self.CfgKey.ROOM, index)

    def get_loc_racks_row(self, index=None):
        """Get location racks row
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Row member or list
        """

        return self._get_members(
            self.cfg.location.racks, self.CfgKey.ROW, index)

    def get_loc_racks_cell(self, index=None):
        """Get location racks cell
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Cell member or list
        """

        return self._get_members(
            self.cfg.location.racks, self.CfgKey.CELL, index)

    def get_depl_netw_mgmt_cnt(self):
        """Get deployer networks mgmt count
        Returns:
            int: Deployer management network count
        """

        return len(self.cfg.deployer.networks.mgmt)

    def get_depl_netw_mgmt_device(self, index=None):
        """Get deployer networks mgmt device
        Args:
            index (int, optional): List index

        Returns:
            str: Network device
        """

        return self._get_members(
            self.cfg.deployer.networks.mgmt,
            self.CfgKey.DEVICE,
            index)

    def yield_depl_netw_mgmt_device(self):
        """Yield deployer networks mgmt device
        Returns:
            iter of str: Network device
        """

        for member in self.get_depl_netw_mgmt_device():
            yield member

    def get_depl_netw_mgmt_intf_ip(self, index=None):
        """Get deployer networks mgmt interface_ipaddr
        Args:
            index (int, optional): List index

        Returns:
            str: Interface IP address
        """

        return self._get_members(
            self.cfg.deployer.networks.mgmt,
            self.CfgKey.INTERFACE_IPADDR,
            index)

    def yield_depl_netw_mgmt_intf_ip(self):
        """Yield deployer networks mgmt interface_ipaddr
        Returns:
            iter of str: Interface IP address
        """

        for member in self.get_depl_netw_mgmt_intf_ip():
            yield member

    def get_depl_netw_mgmt_cont_ip(self, index=None):
        """Get deployer networks mgmt container_ipaddr
        Args:
            index (int, optional): List index

        Returns:
            str: Container IP address
        """

        return self._get_members(
            self.cfg.deployer.networks.mgmt,
            self.CfgKey.CONTAINER_IPADDR,
            index)

    def yield_depl_netw_mgmt_cont_ip(self):
        """Yield deployer networks mgmt container_ipaddr
        Returns:
            iter of str: Container IP address
        """

        for member in self.get_depl_netw_mgmt_cont_ip():
            yield member

    def get_depl_netw_mgmt_brg_ip(self, index=None):
        """Get deployer networks mgmt bridge_ipaddr
        Args:
            index (int, optional): List index

        Returns:
            str: Bridge IP address
        """

        return self._get_members(
            self.cfg.deployer.networks.mgmt, self.CfgKey.BRIDGE_IPADDR, index)

    def yield_depl_netw_mgmt_brg_ip(self):
        """Yield deployer networks mgmt bridge_ipaddr
        Returns:
            iter of str: Bridge IP address
        """

        for member in self.get_depl_netw_mgmt_brg_ip():
            yield member

    def get_depl_netw_mgmt_vlan(self, index=None):
        """Get deployer networks mgmt vlan
        Args:
            index (int, optional): List index

        Returns:
            int: VLAN
        """

        return self._get_members(
            self.cfg.deployer.networks.mgmt, self.CfgKey.VLAN, index)

    def yield_depl_netw_mgmt_vlan(self):
        """Yield deployer networks mgmt vlan
        Returns:
            iter of str: VLAN
        """

        for member in self.get_depl_netw_mgmt_vlan():
            yield member

    def get_depl_netw_mgmt_netmask(self, index=None):
        """Get deployer networks mgmt netmask
        Returns:
            str or iter of str: Netmask
        """

        if index is None:
            list_ = []
            for member in self.cfg.deployer.networks.mgmt:
                if self.CfgKey.NETMASK in member:
                    list_.append(member[self.CfgKey.NETMASK])
                elif self.CfgKey.PREFIX in member:
                    list_.append(self._prefix_to_netmask(
                        member[self.CfgKey.PREFIX]))
                else:
                    self._netmask_prefix_not_found()
            return list_
        else:
            member = self.cfg.deployer.networks.mgmt[index]
            if self.CfgKey.NETMASK in member:
                return member[self.CfgKey.NETMASK]
            elif self.CfgKey.PREFIX in member:
                return self._prefix_to_netmask(member[self.CfgKey.PREFIX])
            else:
                self._netmask_prefix_not_found()

    def yield_depl_netw_mgmt_netmask(self):
        """Yield deployer networks mgmt netmask
        Returns:
            iter of str: Netmask
        """

        for member in self.get_depl_netw_mgmt_netmask():
            yield member

    def get_depl_netw_mgmt_prefix(self, index=None):
        """Get deployer networks mgmt prefix
        Returns:
            str or iter of str: Prefix
        """

        if index is None:
            list_ = []
            for member in self.cfg.deployer.networks.mgmt:
                if self.CfgKey.PREFIX in member:
                    list_.append(member[self.CfgKey.PREFIX])
                elif self.CfgKey.NETMASK in member:
                    list_.append(self._netmask_to_prefix(
                        member[self.CfgKey.NETMASK]))
                else:
                    self._netmask_prefix_not_found()
            return list_
        else:
            member = self.cfg.deployer.networks.mgmt[index]
            if self.CfgKey.PREFIX in member:
                return member[self.CfgKey.PREFIX]
            elif self.CfgKey.NETMASK in member:
                return self._netmask_to_prefix(member[self.CfgKey.NETMASK])
            else:
                self._netmask_prefix_not_found()

    def yield_depl_netw_mgmt_prefix(self):
        """Yield deployer networks mgmt prefix
        Returns:
            iter of str: Prefix
        """

        for member in self.get_depl_netw_mgmt_prefix():
            yield member

    def get_depl_netw_client_cnt(self):
        """Get deployer networks client count
        Returns:
            int: Deployer client network count
        """

        return len(self.cfg.deployer.networks.client)

    def get_depl_netw_client_type(self, index=None):
        """Get deployer networks client type
        Args:
            index (int, optional): List index

        Returns:
            str: Client type (ipmi or pxe)
        """

        return self._get_members(
            self.cfg.deployer.networks.client,
            self.CfgKey.CONTAINER_IPADDR,
            index)

    def yield_depl_netw_client_type(self):
        """Yield deployer networks client type
        Returns:
            iter of str: Network type
        """

        for member in self.get_depl_netw_client_type():
            yield member

    def get_depl_netw_client_device(self, index=None):
        """Get deployer networks client device
        Args:
            index (int, optional): List index

        Returns:
            str: Client type (ipmi or pxe)
        """

        return self._get_members(
            self.cfg.deployer.networks.client,
            self.CfgKey.DEVICE,
            index)

    def yield_depl_netw_client_device(self):
        """Yield deployer networks client device
        Returns:
            iter of str: Network device
        """

        for member in self.get_depl_netw_client_device():
            yield member

    def get_depl_netw_client_intf_ip(self, index=None):
        """Get deployer networks client interface_ipaddr
        Args:
            index (int, optional): List index

        Returns:
            str: Interface IP address
        """

        return self._get_members(
            self.cfg.deployer.networks.client,
            self.CfgKey.INTERFACE_IPADDR,
            index)

    def yield_depl_netw_client_intf_ip(self):
        """Yield deployer networks client interface_ipaddr
        Returns:
            iter of str: Interface IP address
        """

        for member in self.get_depl_netw_client_intf_ip():
            yield member

    def get_depl_netw_client_cont_ip(self, index=None):
        """Get deployer networks client container_ipaddr
        Args:
            index (int, optional): List index

        Returns:
            str: Container IP address
        """

        return self._get_members(
            self.cfg.deployer.networks.client,
            self.CfgKey.CONTAINER_IPADDR,
            index)

    def yield_depl_netw_client_cont_ip(self):
        """Yield deployer networks client container_ipaddr
        Returns:
            iter of str: Container IP address
        """

        for member in self.get_depl_netw_client_cont_ip():
            yield member

    def get_depl_netw_client_brg_ip(self, index=None):
        """Get deployer networks client bridge_ipaddr
        Args:
            index (int, optional): List index

        Returns:
            str: Bridge IP address
        """

        return self._get_members(
            self.cfg.deployer.networks.client,
            self.CfgKey.BRIDGE_IPADDR,
            index)

    def yield_depl_netw_client_brg_ip(self):
        """Yield deployer networks client bridge_ipaddr
        Returns:
            iter of str: Bridge IP address
        """

        for member in self.get_depl_netw_client_brg_ip():
            yield member

    def get_depl_netw_client_vlan(self, index=None):
        """Get deployer networks client vlan
        Args:
            index (int, optional): List index

        Returns:
            int: VLAN
        """

        return self._get_members(
            self.cfg.deployer.networks.client, self.CfgKey.VLAN, index)

    def yield_depl_netw_client_vlan(self):
        """Yield deployer networks client vlan
        Returns:
            iter of str: VLAN
        """

        for member in self.get_depl_netw_client_vlan():
            yield member

    def get_depl_netw_client_netmask(self, index=None):
        """Get deployer networks client netmask
        Returns:
            str or iter of str: Netmask
        """

        if index is None:
            list_ = []
            for member in self.cfg.deployer.networks.client:
                if self.CfgKey.NETMASK in member:
                    list_.append(member[self.CfgKey.NETMASK])
                elif self.CfgKey.PREFIX in member:
                    list_.append(self._prefix_to_netmask(
                        member[self.CfgKey.PREFIX]))
                else:
                    self._netmask_prefix_not_found()
            return list_
        else:
            member = self.cfg.deployer.networks.client[index]
            if self.CfgKey.NETMASK in member:
                return member[self.CfgKey.NETMASK]
            elif self.CfgKey.PREFIX in member:
                return self._prefix_to_netmask(member[self.CfgKey.PREFIX])
            else:
                self._netmask_prefix_not_found()

    def yield_depl_netw_client_netmask(self):
        """Yield deployer networks client netmask
        Returns:
            iter of str: Netmask
        """

        for member in self.get_depl_netw_client_netmask():
            yield member

    def get_depl_netw_client_prefix(self, index=None):
        """Get deployer networks client prefix
        Returns:
            str or iter of str: Prefix
        """

        if index is None:
            list_ = []
            for member in self.cfg.deployer.networks.client:
                if self.CfgKey.PREFIX in member:
                    list_.append(member[self.CfgKey.PREFIX])
                elif self.CfgKey.NETMASK in member:
                    list_.append(self._netmask_to_prefix(
                        member[self.CfgKey.NETMASK]))
                else:
                    self._netmask_prefix_not_found()
            return list_
        else:
            member = self.cfg.deployer.networks.client[index]
            if self.CfgKey.PREFIX in member:
                return member[self.CfgKey.PREFIX]
            elif self.CfgKey.NETMASK in member:
                return self._netmask_to_prefix(member[self.CfgKey.NETMASK])
            else:
                self._netmask_prefix_not_found()

    def yield_depl_netw_client_prefix(self):
        """Yield deployer networks client prefix
        Returns:
            iter of str: Prefix
        """

        for member in self.get_depl_netw_client_prefix():
            yield member

    def get_sw_mgmt_cnt(self):
        """Get switches mgmt count
        Returns:
            int: Management switch count
        """

        return len(self.cfg.switches.mgmt)

    def get_sw_mgmt_index_by_label(self, label):
        """Get switches mgmt index by label
        Returns:
            int: Label index
        """

        for index, mgmt in enumerate(self.cfg.switches.mgmt):
            if label == mgmt.label:
                return index

    def get_sw_mgmt_label(self, index=None):
        """Get switches mgmt label
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Label member or list
        """

        return self._get_members(
            self.cfg.switches.mgmt, self.CfgKey.LABEL, index)

    def yield_sw_mgmt_label(self):
        """Yield switches mgmt label
        Returns:
            iter of str: Label
        """

        for member in self.get_sw_mgmt_label():
            yield member

    def get_sw_mgmt_hostname(self, index=None):
        """Get switches mgmt hostname
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Hostname member or list
        """

        return self._get_members(
            self.cfg.switches.mgmt, self.CfgKey.HOSTNAME, index)

    def yield_sw_mgmt_hostname(self):
        """Yield switches mgmt hostname
        Returns:
            iter of str: Hostname
        """

        for member in self.get_sw_mgmt_hostname():
            yield member

    def get_sw_mgmt_userid(self, index=None):
        """Get switches mgmt userid
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Userid member or list
        """

        return self._get_members(
            self.cfg.switches.mgmt, self.CfgKey.USERID, index)

    def yield_sw_mgmt_userid(self):
        """Yield switches mgmt userid
        Returns:
            iter of str: Userid
        """

        for member in self.get_sw_mgmt_userid():
            yield member

    def get_sw_mgmt_password(self, index=None):
        """Get switches mgmt password
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Password member or list
        """

        return self._get_members(
            self.cfg.switches.mgmt, self.CfgKey.PASSWORD, index)

    def yield_sw_mgmt_password(self):
        """Yield switches mgmt password
        Returns:
            iter of str: Password
        """

        for member in self.get_sw_mgmt_password():
            yield member

    def get_sw_mgmt_ssh_key(self, index=None):
        """Get switches mgmt ssh_key
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: SSH key member or list
        """

        return self._get_members(
            self.cfg.switches.mgmt, self.CfgKey.SSH_KEY, index)

    def yield_sw_mgmt_ssh_key(self):
        """Yield switches mgmt ssh_key
        Returns:
            iter of str: SSH key
        """

        for member in self.get_sw_mgmt_ssh_key():
            yield member

    def get_sw_mgmt_rack_id(self, index=None):
        """Get switches mgmt rack_id
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Rack ID member or list
        """

        return self._get_members(
            self.cfg.switches.mgmt, self.CfgKey.RACK_ID, index)

    def yield_sw_mgmt_rack_id(self):
        """Yield switches mgmt rack_id
        Returns:
            iter of str: Rack ID
        """

        for member in self.get_sw_mgmt_rack_id():
            yield member

    def get_sw_mgmt_rack_eia(self, index=None):
        """Get switches mgmt rack_eia
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Rack EIA member or list
        """

        return self._get_members(
            self.cfg.switches.mgmt, self.CfgKey.RACK_EIA, index)

    def yield_sw_mgmt_rack_eia(self):
        """Yield switches mgmt rack_eia
        Returns:
            iter of str: Rack EIA
        """

        for member in self.get_sw_mgmt_rack_eia():
            yield member

    def get_sw_mgmt_ibintf_cnt(self, switch_index):
        """Get switches mgmt inband_interfaces ipaddr count
        Args:
            switch_index (int): Management switch index

        Returns:
            int: Management switch inband interface count
        """

        return len(self.cfg.switches.mgmt[switch_index].inband_interfaces)

    def get_sw_mgmt_ibintf_ip(self, switch_index, index=None):
        """Get switches mgmt inband_interfaces ipaddr
        Args:
            switch_index (int): Management switch index
            index (int, optional): List index

        Returns:
            str or list of str: IP address member or list
        """
        return self._get_members(
            self.cfg.switches.mgmt[switch_index].inband_interfaces,
            self.CfgKey.IPADDR, index)

    def yield_sw_mgmt_ibintf_ip(self, switch_index):
        """Yield switches mgmt inband_interfaces ipaddr
        Args:
            switch_index (int): Management switch index

        Returns:
            iter of str: IP address
        """

        for member in self.get_sw_mgmt_ibintf_ip(switch_index):
            yield member

    def get_sw_mgmt_ibintf_ports(self, switch_index, index=None):
        """Get switches mgmt inband_interfaces ports
        Args:
            switch_index (int): Management switch index
            index (int, optional): List index

        Returns:
            int or list of int: Port member or list
        """
        return self._get_members(
            self.cfg.switches.mgmt[switch_index].inband_interfaces,
            self.CfgKey.PORT, index)

    def yield_sw_mgmt_ibintf_ports(self, switch_index):
        """Yield switches mgmt inband_interfaces ports
        Args:
            switch_index (int): Management switch index

        Returns:
            iter of int: Port
        """

        for member in self.get_sw_mgmt_ibintf_ports(switch_index):
            yield member

    def get_sw_data_cnt(self):
        """Get switches data count
        Returns:
            int: Data switch count
        """

        return len(self.cfg.switches.data)

    def get_sw_data_label(self, index=None):
        """Get switches data label
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Label member or list
        """

        return self._get_members(
            self.cfg.switches.data, self.CfgKey.LABEL, index)

    def yield_sw_data_label(self):
        """Yield switches data label
        Returns:
            iter of str: Label
        """

        for member in self.get_sw_data_label():
            yield member

    def get_sw_data_hostname(self, index=None):
        """Get switches data hostname
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Hostname member or list
        """

        return self._get_members(
            self.cfg.switches.data, self.CfgKey.HOSTNAME, index)

    def yield_sw_data_hostname(self):
        """Yield switches data hostname
        Returns:
            iter of str: Hostname
        """

        for member in self.get_sw_data_hostname():
            yield member

    def get_sw_data_userid(self, index=None):
        """Get switches data userid
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Userid member or list
        """

        return self._get_members(
            self.cfg.switches.data, self.CfgKey.USERID, index)

    def yield_sw_data_userid(self):
        """Yield switches data userid
        Returns:
            iter of str: Userid
        """

        for member in self.get_sw_data_userid():
            yield member

    def get_sw_data_password(self, index=None):
        """Get switches data password
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Password member or list
        """

        return self._get_members(
            self.cfg.switches.data, self.CfgKey.PASSWORD, index)

    def yield_sw_data_password(self):
        """Yield switches data password
        Returns:
            iter of str: Password
        """

        for member in self.get_sw_data_password():
            yield member

    def get_sw_data_ssh_key(self, index=None):
        """Get switches data ssh_key
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: SSH key member or list
        """

        return self._get_members(
            self.cfg.switches.data, self.CfgKey.SSH_KEY, index)

    def yield_sw_data_ssh_key(self):
        """Yield switches data ssh_key
        Returns:
            iter of str: SSH key
        """

        for member in self.get_sw_data_ssh_key():
            yield member

    def get_ntmpl_cnt(self):
        """Get node_templates count
        Returns:
            int: Node template count
        """

        return len(self.cfg.node_templates)

    def yield_ntmpl_ind(self):
        """Yield node_templates iindex
        Returns:
            int: Node template index
        """

        for index in range(0, self.get_ntmpl_cnt()):
            yield index

    def get_ntmpl_label(self, index=None):
        """Get node_templates label
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Type member or list
        """

        return self._get_members(
            self.cfg.node_templates, self.CfgKey.LABEL, index)

    def yield_ntmpl_label(self):
        """Yield node_templates label
        Returns:
            iter of str: Type
        """

        for member in self.get_ntmpl_label():
            yield member

    def get_ntmpl_ipmi_userid(self, index=None):
        """Get node_templates ipmi userid
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: IPMI userid member or list
        """
        if index is None:
            list_ = []
            for member in self.cfg.node_templates:
                list_.append(member.ipmi.userid)
            return list_
        return self.cfg.node_templates[index].ipmi.userid

    def yield_ntmpl_ipmi_userid(self):
        """Yield node_templates ipmi userid
        Returns:
            iter of str: IPMI userid
        """

        for member in self.get_ntmpl_ipmi_userid():
            yield member

    def get_ntmpl_ipmi_password(self, index=None):
        """Get node_templates ipmi password
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: IPMI password member or list
        """
        if index is None:
            list_ = []
            for member in self.cfg.node_templates:
                list_.append(member.ipmi.password)
            return list_
        return self.cfg.node_templates[index].ipmi.password

    def yield_ntmpl_ipmi_password(self):
        """Yield node_templates ipmi password
        Returns:
            iter of str: IPMI password
        """

        for member in self.get_ntmpl_ipmi_password():
            yield member

    def get_ntmpl_os_hostname_prefix(self, index=None):
        """Get node_templates os hostname_prefix
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: Hostname prefix member or list
        """
        if index is None:
            list_ = []
            for member in self.cfg.node_templates:
                if self.CfgKey.HOSTNAME_PREFIX in member.os.iterkeys():
                    list_.append(member.os.hostname_prefix)
                else:
                    list_.append(None)
            return list_
        if (self.CfgKey.HOSTNAME_PREFIX in
                self.cfg.node_templates[index].os.iterkeys()):
            return self.cfg.node_templates[index].os.hostname_prefix

    def yield_ntmpl_os_hostname_prefix(self):
        """Yield node_templates os hostname_prefix
        Returns:
            iter of str: Hostname prefix
        """

        for member in self.get_ntmpl_os_hostname_prefix():
            yield member

    def get_ntmpl_os_profile(self, index=None):
        """Get node_templates os profile
        Args:
            index (int, optional): List index

        Returns:
            str or list of str: OS profile member or list
        """
        if index is None:
            list_ = []
            for member in self.cfg.node_templates:
                list_.append(member.os.profile)
            return list_
        return self.cfg.node_templates[index].os.profile

    def yield_ntmpl_os_profile(self):
        """Yield node_templates os profile
        Returns:
            iter of str: OS profile
        """

        for member in self.get_ntmpl_os_profile():
            yield member

    def get_ntmpl_roles_cnt(self, node_template_index):
        """Get node_templates roles count
        Args:
            node_template_index (int): Node template index

        Returns:
            int: Role count
        """

        return len(self.cfg.node_templates[node_template_index].roles)

    def get_ntmpl_roles(self, node_template_index, index=None):
        """Get node_templates roles
        Args:
            node_template_index (int): Node template index
            index (int, optional): List index

        Returns:
            str or list of str: Role member or list
        """

        if index is None:
            return self.cfg.node_templates[node_template_index].roles
        return self.cfg.node_templates[node_template_index].roles[index]

    def yield_ntmpl_roles(self, node_template_index):
        """Yield node_templates roles
        Args:
            node_template_index (int): Node template index

        Returns:
            iter of str: Role
        """

        for member in self.get_ntmpl_roles(node_template_index):
            yield member

    def get_ntmpl_netw_cnt(self, node_template_index):
        """Get node_templates networks count
        Args:
            node_template_index (int): Node template index

        Returns:
            int: Network count
        """

        return len(self.cfg.node_templates[node_template_index].networks)

    def get_ntmpl_netw(self, node_template_index, index=None):
        """Get node_templates networks
        Args:
            node_template_index (int): Node template index
            index (int, optional): List index

        Returns:
            str or list of str: Network member or list
        """

        if index is None:
            return self.cfg.node_templates[node_template_index].networks
        return self.cfg.node_templates[node_template_index].networks[index]

    def yield_ntmpl_netw(self, node_template_index):
        """Yield node_templates networks
        Args:
            node_template_index (int): Node template index

        Returns:
            iter of str: Network
        """

        for member in self.get_ntmpl_netw(node_template_index):
            yield member

    def get_ntmpl_intf_cnt(self, node_template_index):
        """Get node_templates interfaces count
        Args:
            node_template_index (int): Node template index

        Returns:
            int: Interface count
        """

        return len(self.cfg.node_templates[node_template_index].interfaces)

    def get_ntmpl_intf(self, node_template_index, index=None):
        """Get node_templates interfaces
        Args:
            node_template_index (int): Node template index
            index (int, optional): List index

        Returns:
            str or list of str: Interface member or list
        """

        if index is None:
            return self.cfg.node_templates[node_template_index].interfaces
        return self.cfg.node_templates[node_template_index].interfaces[index]

    def yield_ntmpl_intf(self, node_template_index):
        """Yield node_templates interfaces
        Args:
            node_template_index (int): Node template index

        Returns:
            iter of str: Interface
        """

        for member in self.get_ntmpl_intf(node_template_index):
            yield member

    def get_ntmpl_phyintf_ipmi_cnt(self, node_template_index):
        """Get node_templates physical_interfaces ipmi count
        Args:
            node_template_index (int): Node template index

        Returns:
            int: IPMI count
        """

        node_template = self.cfg.node_templates[node_template_index]
        return len(node_template.physical_interfaces.ipmi)

    def yield_ntmpl_phyintf_ipmi_ind(self, node_template_index):
        """Yield node_templates physical_interfaces ipmi index
        Args:
            node_template_index (int): Node template index

        Returns:
            int: IPMI index
        """

        for index in range(0, self.get_ntmpl_phyintf_ipmi_cnt(
                node_template_index)):
            yield index

    def get_ntmpl_phyintf_ipmi_switch(
            self, node_template_index, index=None):
        """Get node_templates physical_interfaces ipmi switch
        Args:
            node_template_index (int): Node template index
            index (int, optional): List index

        Returns:
            str or list of str: IPMI switch member or list
        """

        node_template = self.cfg.node_templates[node_template_index]
        return self._get_members(
            node_template.physical_interfaces.ipmi, self.CfgKey.SWITCH, index)

    def yield_ntmpl_phyintf_ipmi_switch(self, node_template_index):
        """Yield node_templates physical_interfaces ipmi switch
        Args:
            node_template_index (int): Node template index

        Returns:
            iter of str: IPMI switch
        """

        for member in self.get_ntmpl_phyintf_ipmi_switch(node_template_index):
            yield member

    def get_ntmpl_phyintf_ipmi_pt_cnt(self, node_template_index, ipmi_index):
        """Get node template physical interface IPMI ports count
        Args:
            node_template_index (int): Node template index
            ipmi_index (int): IPMI index

        Returns:
            int: IPMI ports count
        """

        node_template = self.cfg.node_templates[node_template_index]
        return len(node_template.physical_interfaces.ipmi[ipmi_index].ports)

    def yield_ntmpl_phyintf_ipmi_pt_ind(
            self, node_template_index, ipmi_index):
        """Yield node template physical interface IPMI ports index
        Returns:
            int: IPMI ports index
        """

        for index in range(0, self.get_ntmpl_phyintf_ipmi_pt_cnt(
                node_template_index, ipmi_index)):
            yield index

    def get_ntmpl_phyintf_ipmi_ports(
            self, node_template_index, ipmi_index, index=None):
        """Get node_templates physical_interfaces ipmi ports
        Args:
            node_template_index (int): Node template index
            ipmi_index (int): IPMI index
            index (int, optional): List index

        Returns:
            int or list of int: IPMI ports member or list
        """

        node_template = self.cfg.node_templates[node_template_index]
        if index is None:
            return node_template.physical_interfaces.ipmi[ipmi_index].ports
        return node_template.physical_interfaces.ipmi[ipmi_index].ports[index]

    def yield_ntmpl_phyintf_ipmi_ports(self, node_template_index, ipmi_index):
        """Yield node_templates physical_interfaces ipmi ports
        Args:
            node_template_index (int): Node template index
            ipmi_index (int): IPMI index

        Returns:
            iter of int: IPMI ports
        """

        for member in self.get_ntmpl_phyintf_ipmi_ports(
                node_template_index, ipmi_index):
            yield member

    def get_ntmpl_phyintf_pxe_cnt(self, node_template_index):
        """
        Args:
            node_template_index (int): Node template index

        Returns:
            int: PXE count
        """

        node_template = self.cfg.node_templates[node_template_index]
        return len(node_template.physical_interfaces.pxe)

    def get_ntmpl_phyintf_pxe_switch(
            self, node_template_index, index=None):
        """Get node_templates physical_interfaces pxe switch
        Args:
            node_template_index (int): Node template index
            index (int, optional): List index

        Returns:
            str or list of str: PXE switch member or list
        """

        node_template = self.cfg.node_templates[node_template_index]
        return self._get_members(
            node_template.physical_interfaces.pxe, self.CfgKey.SWITCH, index)

    def yield_ntmpl_phyintf_pxe_switch(self, node_template_index):
        """Yield node_templates physical_interfaces pxe switch
        Args:
            node_template_index (int): Node template index

        Returns:
            iter of str: PXE switch
        """

        for member in self.get_ntmpl_phyintf_pxe_switch(node_template_index):
            yield member

    def get_ntmpl_phyintf_pxe_dev(
            self, node_template_index, index=None):
        """Get node_templates physical_interfaces pxe dev
        Args:
            node_template_index (int): Node template index
            index (int, optional): List index

        Returns:
            str or list of str: PXE dev member or list
        """

        node_template = self.cfg.node_templates[node_template_index]
        return self._get_members(
            node_template.physical_interfaces.pxe, self.CfgKey.DEVICE, index)

    def yield_ntmpl_phyintf_pxe_dev(self, node_template_index):
        """Yield node_templates physical_interfaces pxe dev
        Args:
            node_template_index (int): Node template index

        Returns:
            iter of str: PXE dev
        """

        for member in self.get_ntmpl_phyintf_pxe_dev(node_template_index):
            yield member

    def get_ntmpl_phyintf_pxe_pt_cnt(self, node_template_index, pxe_index):
        """
        Args:
            node_template_index (int): Node template index
            pxe_index (int): PXE index

        Returns:
            int: PXE ports count
        """

        node_template = self.cfg.node_templates[node_template_index]
        return len(node_template.physical_interfaces.pxe[pxe_index].ports)

    def yield_ntmpl_phyintf_pxe_pt_ind(self, node_template_index, pxe_index):
        """Yield node template physical interface PXE ports count
        Returns:
            int: PXE ports index
        """

        for index in range(0, self.get_ntmpl_phyintf_pxe_pt_cnt(
                node_template_index, pxe_index)):
            yield index

    def get_ntmpl_phyintf_pxe_ports(
            self, node_template_index, pxe_index, index=None):
        """Get node_templates physical_interfaces pxe ports
        Args:
            node_template_index (int): Node template index
            pxe_index (int): PXE index
            index (int, optional): List index

        Returns:
            int or list of int: PXE ports member or list
        """

        node_template = self.cfg.node_templates[node_template_index]
        if index is None:
            return node_template.physical_interfaces.pxe[pxe_index].ports
        return node_template.physical_interfaces.pxe[pxe_index].ports[index]

    def yield_ntmpl_phyintf_pxe_ports(self, node_template_index, pxe_index):
        """Yield node_templates physical_interfaces pxe ports
        Args:
            node_template_index (int): Node template index
            pxe_index (int): PXE index

        Returns:
            iter of int: PXE ports
        """

        for member in self.get_ntmpl_phyintf_pxe_ports(
                node_template_index, pxe_index):
            yield member
