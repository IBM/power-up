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

from lib.ssh import SSH
from lib.SwitchException import SwitchException
import switch_common
import re


class Lenovo(switch_common.SwitchCommon):

    SHOW_VLAN = 'show vlan %d'
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

    def __init__(self, log, ip_addr, userid, password):
        switch_common.SwitchCommon.__init__(self, log, ip_addr, userid, password)

    def send_cmd(self, cmd):
        ssh = SSH(self.log)
        _, data, _ = ssh.exec_cmd(
            self.ip_addr,
            self.userid,
            self.password,
            cmd,
            ssh_log=self.ssh_log,
            look_for_keys=False)
        return data

    def show_vlans(self):
        vlan_info = self.send_cmd(self.SHOW_VLAN)
        return vlan_info

    def show_mac_address_table(self):
        mac_info = self.send_cmd(self.SHOW_MAC_ADDRESS_TABLE)
        return mac_info

    def create_vlan(self, vlan):
        self.send_cmd(
            self.ENABLE_REMOTE_CONFIG %
            (self.CREATE_VLAN % (self.vlan)))
        if self.is_vlan_created(vlan):
            self.log.info(
                'Created management client VLAN %s' %
                (self.vlan))
        else:
            raise SwitchException(
                'Failed creating management client VLAN %s' %
                (self.vlan))

    def set_native_vlan_for_port(self, vlan, port):
        self.send_cmd(
            self.ENABLE_REMOTE_CONFIG %
            (self.ADD_VLAN_TO_ACCESS_PORT % (port, vlan)))
        if self.is_vlan_allowed_for_port(vlan, port):
            self.log.info(
                'Added management VLAN %s to access port %s' %
                (vlan, port))
        else:
            raise SwitchException(
                'Failed adding management VLAN %s to access port %s' %
                (vlan, port))

    def is_port_in_trunk_mode(self, port):
        if re.search(
                r'^\S+\s+' + str(port) + r'\s+y',
                self.send_cmd(self.SHOW_INTERFACE_TRUNK % (port)),
                re.MULTILINE):
            return True
        return False

    def is_port_in_access_mode(self, port):
        if self.is_port_in_trunk_mode(port):
            return False
        return True

    def is_vlan_created(self, vlan):
        if re.search(
                '^' + str(vlan),
                self.send_cmd(self.SHOW_VLAN % (vlan)),
                re.MULTILINE):
            return True
        return False

    def is_vlan_allowed_for_port(self, vlan, port):
        pattern = re.compile(r'^\s+VLANs:(.+)', re.MULTILINE)
        match = pattern.search(
            self.send_cmd(self.SHOW_ALLOWED_VLANS % (port)))
        if match:
            if str(vlan) in re.split(',| ', match.group(1)):
                return True
        return False


class switch(object):
    @staticmethod
    def factory(log, ip_addr, userid, password):
            return Lenovo(log, ip_addr, userid, password)
