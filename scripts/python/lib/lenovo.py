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

import re
import os.path

from lib.SwitchException import SwitchException
import switch_common
from lib.genesis import gen_passive_path, gen_path


class Lenovo(switch_common.SwitchCommon):
    """Class for configuring and retrieving information for a Lenovo
    switch.  This class works with the Lenovo G8052.  Similar
    Lenovo switches may work or may need some methods overridden.
    This class can be instantiated in 'active' mode, in which case the
    switch will be configured or in 'passive' mode in which case the
    commands needed to configure the switch are written to a file.
    When in passive mode, information requests will return 'None'.
    In passive mode, a filename can be supplied which
    will contain the active mode switch commands used for switch
    configuration. This outfile will be written to the
    'cluster-genesis/passive' directory if it exists or to the
    'cluster-genesies' directory if the passive diectory does not
    exist. If no outfile name is provided a default name is used.
    In active mode, the 'ip_addr, userid and password named variables
    are required. If 'mode' is not provided, it is defaulted to 'passive'.

    Args:
        log (:obj:`Logger`): Log file object.
        ip_addr (string): Switch management interface IP address.
        userid (string): Switch management interface login user ID.
        password (string): Switch management interface login password.
        mode (string): Set to 'passive' to run in passive switch mode.
            Defaults to 'active'
        outfile (string): Name of file to direct switch output to.
    """
    SHOW_VLAN = 'show vlan'
    SHOW_INTERFACE_TRUNK = 'show interface trunk | include %d'
    SHOW_ALLOWED_VLANS = 'show interface port %d | include VLANs'
    SHOW_MAC_ADDRESS_TABLE = 'show mac-address-table;'
    ENABLE_REMOTE_CONFIG = 'enable;configure terminal; %s'
    CREATE_VLAN = 'vlan %d'
    ADD_VLAN_TO_TRUNK_PORT = (
        'interface port %d'
        ';switchport mode trunk'
        ';switchport trunk allowed vlan add %d')
    SET_NATIVE_VLAN = (
        'interface port %d'
        ';switchport access vlan %d')
    SHOW_NATIVE_VLAN = (
        'show interface trunk | include %d')
    SET_SWITCHPORT_MODE = (
        ENABLE_REMOTE_CONFIG %
        'no prompting'
        ';interface port %d'
        ';switchport mode %s'
        ';exit'
        ';prompting')
    CLEAR_MAC_ADDRESS_TABLE = (
        ENABLE_REMOTE_CONFIG %
        'clear mac-address-table')

    def __init__(self, log, ip_addr=None, userid=None, password=None, mode=None, outfile=None):
        self.mode = mode
        self.log = log
        if self.mode == 'active':
            self.ip_addr = ip_addr
            self.userid = userid
            self.password = password
        elif self.mode == 'passive':
            if os.path.isdir(gen_passive_path):
                self.outfile = gen_passive_path + '/' + outfile
            else:
                self.outfile = gen_path + '/' + outfile
            self.outfile = gen_passive_path + str('/') + str(outfile)
        switch_common.SwitchCommon.__init__(self, log, ip_addr, userid, password, mode, outfile)

    def show_vlans(self):
        if self.mode == 'passive':
            return None
        vlan_info = self.send_cmd(self.SHOW_VLAN)
        return vlan_info

    def show_native_vlan(self, port):
        if self.mode == 'passive':
            return None
        vlan = self.send_cmd(self.SHOW_NATIVE_VLAN % port)
        vlan = re.search(
            r'^\d+ +' + str(port) + '[ +\w+]+', vlan, re.MULTILINE)
        vlan = vlan.group()
        vlan = re.findall(r'\w+', vlan)[7]
        return int(vlan)

    def show_mac_address_table(self, format=False):
        """Get switch mac address table.

        The returned text string can be raw or optionally fomatted.

        Args:
            format (boolean) : set to 'dict' to return a dictioanry
            mac address table. Keys are int port numebers, values
            are lists of mac addreses.
        Returns:
            raw string if format=False
            dictionary of ports and mac address values if format='dict'.
        """
        if self.mode == 'passive':
            if format == 'dict':
                return {}
            return None
        mac_info = self.send_cmd(self.SHOW_MAC_ADDRESS_TABLE)
        if not format:
            return mac_info
        if format == 'dict':
            return self.get_mac_dict(mac_info)

    def create_vlan(self, vlan):
        self.send_cmd(
            self.ENABLE_REMOTE_CONFIG %
            (self.CREATE_VLAN % (self.vlan)))
        if self.mode == 'passive':
            return
        if self.is_vlan_created(vlan):
            self.log.info(
                'Created management client VLAN %s' %
                (self.vlan))
        else:
            raise SwitchException(
                'Failed creating management client VLAN %s' %
                (self.vlan))

    def clear_mac_address_table(self):
        self.send_cmd(self.CLEAR_MAC_ADDRESS_TABLE)

    def add_vlan_to_trunk_port(self, vlan, port):
        self.send_cmd(
            self.ENABLE_REMOTE_CONFIG %
            (self.ADD_VLAN_TO_TRUNK_PORT % (port, vlan)))
        if self.is_vlan_allowed_for_port(vlan, port):
            self.log.info(
                'Added management VLAN %s to access port %s' %
                (vlan, port))
        else:
            raise SwitchException(
                'Failed adding management VLAN %s to access port %s' %
                (vlan, port))

    def set_switchport_native_vlan(self, vlan, port):
        self.send_cmd(
            self.ENABLE_REMOTE_CONFIG %
            (self.SET_NATIVE_VLAN % (port, vlan)))
        if self.mode == 'passive':
            return
        if vlan == self.show_native_vlan(port):
            self.log.info(
                'Set native VLAN to %s for access port %s' %
                (vlan, port))
        else:
            raise SwitchException(
                'Failed adding management VLAN %s to access port %s' %
                (vlan, port))

    def set_switchport_mode(self, mode, port):
        self.send_cmd(self.SET_SWITCHPORT_MODE % (port, mode))
        if self.mode == 'passive':
            return
        if self.is_port_in_trunk_mode(port) and mode == 'trunk':
            self.log.info(
                'Set port %s to %s mode' %
                (port, mode))
        elif self.is_port_in_access_mode(port) and mode == 'access':
            self.log.info(
                'Set port %s to %s mode' %
                (port, mode))
        else:
            raise SwitchException(
                'Failed setting port %s to %s mode' %
                (port, mode))

    def is_port_in_trunk_mode(self, port):
        if self.mode == 'passive':
            return None
        if re.search(
                r'^\S+\s+' + str(port) + r'\s+y',
                self.send_cmd(
                    self.SHOW_INTERFACE_TRUNK %
                    (port)), re.MULTILINE):
            return True
        return False

    def is_port_in_access_mode(self, port):
        if self.mode == 'passive':
            return None
        if self.is_port_in_trunk_mode(port):
            return False
        return True

    def is_vlan_created(self, vlan):
        if self.mode == 'passive':
            return None
        if re.search(
                '^' + str(vlan),
                self.send_cmd(self.SHOW_VLAN % (vlan)),
                re.MULTILINE):
            return True
        return False

    def is_vlan_allowed_for_port(self, vlan, port):
        if self.mode == 'passive':
            return None
        pattern = re.compile(r'^\s+VLANs:(.+)', re.MULTILINE)
        match = pattern.search(
            self.send_cmd(self.SHOW_ALLOWED_VLANS % (port)))
        if match:
            if str(vlan) in re.split(',| ', match.group(1)):
                return True
        return False


class switch(object):
    @staticmethod
    def factory(log, ip_addr=None, userid=None, password=None, mode=None, outfile=None):
        return Lenovo(log, ip_addr, userid, password, mode, outfile)
