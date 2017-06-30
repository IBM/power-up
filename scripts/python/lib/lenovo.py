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
import datetime

from lib.switch_exception import SwitchException
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
    In passive mode, a filename can be generated which
    will contain the active mode switch commands used for switch
    configuration. This outfile will be written to the
    'cluster-genesis/passive' directory if it exists or to the
    'cluster-genesies' directory if the passive directory does not
    exist. If no outfile name is provided a default name is used.
    In active mode, the 'host, userid and password named variables
    are required. If 'mode' is not provided, it is defaulted to 'passive'.

    Args:
        log (:obj:`Logger`): Log file object.
        host (string): Management switch management interface IP address
        or hostname or if in passive mode, a fully qualified filename of the
        acquired mac address table for the switch.
        userid (string): Switch management interface login user ID.
        password (string): Switch management interface login password.
        mode (string): Set to 'passive' to run in passive switch mode.
            Defaults to 'active'
        outfile (string): Name of file to direct switch output to when
        in passive mode.
    """
    ENABLE_REMOTE_CONFIG = switch_common.SwitchCommon.ENABLE_REMOTE_CONFIG
    # override ENABLE_REMOTE_CONFIG as needed.
    # ENABLE_REMOTE_CONFIG = 'enable;configure terminal; %s'
    # override as needed per switch syntax:
    # SHOW_VLANS = 'show vlan'
    # override as needed.
    # SHOW_MAC_ADDRESS_TABLE = 'show mac-address-table;'
    # override as needed:
    # CREATE_VLAN = 'vlan %d'
    # override as needed:
    # DELETE_VLAN = 'no vlan %d'
    # override as needed:
    # CLEAR_MAC_ADDRESS_TABLE = (
    #    ENABLE_REMOTE_CONFIG %
    #    'clear mac-address-table')
    SHOW_INTERFACE_TRUNK = 'show interface trunk | include %d'
    SHOW_ALLOWED_VLANS = 'show interface port %d | include VLANs'
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
    SET_INTERFACE_IPADDR = (
        ENABLE_REMOTE_CONFIG % 'interface ip %d;ip address %s')
    SET_INTERFACE_MASK = ENABLE_REMOTE_CONFIG % 'interface ip %d;ip netmask %s'
    SET_VLAN = 'vlan %d'
    SET_INTERFACE_VLAN = ENABLE_REMOTE_CONFIG % 'interface ip %d;' + SET_VLAN
    ENABLE_INTERFACE = ENABLE_REMOTE_CONFIG % 'interface ip %d;enable'
    REMOVE_MGMT_IFC = ENABLE_REMOTE_CONFIG % 'no interface ip %d'
    SHOW_INTERFACE_IP = 'show interface ip '
    UP_STATE_MGMT_IFC = 'up'
    MAX_INTF = 128

    def __init__(self, log, host=None, userid=None, password=None, mode=None, outfile=None):
        self.mode = mode
        self.log = log
        self.host = host
        if self.mode == 'active':
            self.userid = userid
            self.password = password
        elif self.mode == 'passive':
            if os.path.isdir(gen_passive_path):
                self.outfile = gen_passive_path + '/' + outfile
            else:
                self.outfile = gen_path + '/' + outfile
            f = open(self.outfile, 'a+')
            f.write(str(datetime.datetime.now()) + '\n')
            f.close()
        switch_common.SwitchCommon.__init__(self, log, host, userid, password, mode, outfile)

    def show_native_vlan(self, port):
        if self.mode == 'passive':
            return None
        vlan = self.send_cmd(self.SHOW_NATIVE_VLAN % port)
        vlan = re.search(
            r'^\d+ +' + str(port) + '[ +\w+]+', vlan, re.MULTILINE)
        vlan = vlan.group()
        vlan = re.findall(r'\w+', vlan)[7]
        return int(vlan)

    def add_vlan_to_trunk_port(self, vlan, port):
        self.send_cmd(
            self.ENABLE_REMOTE_CONFIG %
            (self.ADD_VLAN_TO_TRUNK_PORT % (port, vlan)))
        if self.is_vlan_allowed_for_port(vlan, port):
            self.log.info(
                'Management VLAN %s is allowed for port %s' %
                (vlan, port))
        else:
            raise SwitchException(
                'Failed adding management VLAN %s to port %s' %
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

    def remove_mgmt_interface(self, intf):
        self.send_cmd(self.REMOVE_MGMT_IFC % intf)

    def _check_interface(self, intf, interfaces, host, netmask, vlan):
        match = re.search(
            r'^%d:\s+IP4\s+\S+\s+(\S+)\s+(\S+),\s+vlan\s(\S+),\s+(\S+)' % intf,
            interfaces,
            re.MULTILINE)
        if not match:
            self.log.error('Misconfigured switch interface %d' % intf)
            return False
        mask = match.group(1)
        _vlan = match.group(3)
        state = match.group(4)

        if mask != netmask:
            self.log.error(
                'Invalid switch mask %s for interface %d' %
                (mask, intf))
            return False
        if _vlan != str(vlan):
            self.log.error(
                'Invalid switch VLAN %s for interface %d' %
                (vlan, intf))
            return False
        if state != self.UP_STATE_MGMT_IFC:
            self.log.error(
                'Switch interface %d is %s' % (intf, state))
            return False
        return True

    def _get_available_interface(self):
        intf = 0
        interfaces = self.send_cmd(self.SHOW_INTERFACE_IP)
        while intf < self.MAX_INTF:
            intf += 1
            match = re.search(
                r'^%d:\s+IP4\s+' % intf,
                interfaces,
                re.MULTILINE)
            if match:
                continue
            return intf

    def configure_mgmt_interface(self, host, netmask, vlan=None, intf=None):
        """Configures a management interface. Minimally, this method will
        configure (overwrite if necessary) the specified interface.
        A better behaved implementation will check if host ip is already in
        use. If it is, it checks to see if it is configured as specified. If
        not, an exception is raised. If no interface number is specified,
        it will use the next available unconfigured interface. The specified
        vlan will be created if it does not already exist.

        Args:
            host (string): hostname or ipv4 address in dot decimal notation
            netmask (string): netmask in dot decimal notation
            vlan (string): Optional. string representation of integer between
            1 and 4094. If none specified, usually the default vlan is used.
            intf (string): optional. String representation of integer between
            1 and 128.
        raises:
            SwitchException if unable to program interface
        """
        interfaces = self.show_mgmt_interfaces()
        match = re.search(
            r'^(\d+):\s+IP4\s+(%s)\s+(\S+)\s+\S+\s+vlan (\d+)' % host,
            interfaces, re.MULTILINE)
        if match:
            intf = int(match.group(1))
            host = match.group(2)
            netmask = match.group(3)
            vlan = int(match.group(4))
            self.log.info('Switch interface %d already configured' % intf)
            if not self._check_interface(intf, interfaces, host, netmask, vlan):
                raise SwitchException(
                    'Conflicting ip Address %s already in use.' % host)
            return
        if vlan is not None:
            self.create_vlan(vlan)
        if intf is None:
            intf = self._get_available_interface()
        self.send_cmd(self.SET_INTERFACE_IPADDR % (intf, host))
        self.send_cmd(self.SET_INTERFACE_MASK % (intf, netmask))
        self.send_cmd(self.SET_INTERFACE_VLAN % (intf, vlan))
        self.send_cmd(self.ENABLE_INTERFACE % intf)
        interfaces = self.show_mgmt_interfaces()
        if not self._check_interface(intf, interfaces, host, netmask, vlan):
            raise SwitchException(
                'Failed configuraing management interface ip %s' % intf)
        return

    def show_mgmt_interfaces(self):
        ifc_info = self.send_cmd(self.SHOW_INTERFACE_IP)
        return ifc_info

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

    def is_vlan_allowed_for_port(self, vlan, port):
        if self.mode == 'passive':
            return None
        vlans = self.send_cmd(self.SHOW_ALLOWED_VLANS % (port))
        vlans = re.search(r'^\s+VLANs: (.+)', vlans, re.MULTILINE).group(1)
        if vlans:
            for vlanrange in vlans.split(','):
                if int(vlanrange.split('-')[0]) <= vlan and \
                        vlan <= int(vlanrange.split('-')[-1]):
                    return True
        return False


class switch(object):
    @staticmethod
    def factory(log, host=None, userid=None, password=None, mode=None, outfile=None):
        return Lenovo(log, host, userid, password, mode, outfile)
