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
import switch_common

from lib.genesis import gen_passive_path, gen_path
from orderedattrdict import AttrDict
from lib.switches import PassiveSwitch


class Mellanox(switch_common.SwitchCommon):
    """Class for configuring and retrieving information for a Mellanox
    switch. Similar Mellanox switches may work or may need some methods
    overridden. This class can be instantiated in 'active' mode, in which
    case the switch will be configured or in 'passive' mode in which case the
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
    ENABLE_REMOTE_CONFIG = 'cli enable "configure terminal" "%s"'
    FORCE = 'force'
    SET_VLAN = 'vlan %d'
    SET_MTU = 'mtu %d'
    INTERFACE_ETHERNET = 'interface ethernet 1/%s'
    SWITCHPORT_MODE_HYBRID = 'switchport mode hybrid'
    SWITCHPORT_HYBRID_ALLOWED_VLAN = \
        'switchport hybrid allowed-vlan add %d'
    SHUTDOWN = 'shutdown'
    NO_SHUTDOWN = 'no shutdown'
    IP_ROUTING = 'ip routing'
    ENABLE_LACP = 'lacp'
    QOS_ENABLE = 'dcb priority-flow-control enable force'
    MLAG = 'protocol mlag'
    LAG_PORT_CHANNEL = 'interface port-channel %d'
    LACP = 'channel-group %d mode active'
    IPL = 'ipl 1'
    QOS_ON = 'dcb priority-flow-control mode on force'
    INTERFACE_VLAN = 'interface vlan %d'
    IP_CIDR = 'ip address %s'
    PEER_ADDR = 'peer-address %s'
    MLAG_VIP = 'mlag-vip my-mlag-vip-domain ip %s force'
    ENABLE_MLAG = 'no mlag shutdown'
    MLAG_PORT_CHANNEL = 'interface mlag-port-channel %d'
    STP_PORT_TYPE_EDGE = 'spanning-tree port type edge'
    STP_BPDUFILTER_ENABLE = 'spanning-tree bpdufilter enable'
    MLAG_ACTIVE = 'mlag-channel-group %d mode active'
    NO_CHANNEL_GROUP = 'no channel-group'
    MAC_RE = re.compile('([\da-fA-F]{2}:){5}([\da-fA-F]{2})')
    CLEAR_MAC_ADDRESS_TABLE = 'clear mac-address-table dynamic'

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
        print("mellanox: show_native_vlan not implemented yet")

    def add_vlan_to_trunk_port(self, vlan, port):
        print("mellanox: add_vlan_to_trunk_port not implemented yet")

    def set_switchport_native_vlan(self, vlan, port):
        print("mellanox: set_switchport_native_vlan not implemented yet")

    def set_switchport_mode(self, mode, port):
        print("mellanox: set_switchport_mode not implemented yet")

    def remove_interface(self, intf):
        print("mellanox: remove_interface not implemented yet")

    def _check_interface(self, intf, interfaces, host, netmask, vlan):
        print("mellanox: _check_interface not implemented yet")

    def _get_available_interface(self):
        print("mellanox: _get_available_interface not implemented yet")

    def configure_interface(self, host, netmask, vlan=None, intf=None):
        print("mellanox: configure_interface not implemented yet")

    def show_interfaces(self):
        print("mellanox: show_interfaces not implemented yet")

    def is_port_in_trunk_mode(self, port):
        print("mellanox: is_port_in_trunk_mode not implemented yet")

    def is_port_in_access_mode(self, port):
        print("mellanox: is_port_in_access_mode not implemented yet")

    def is_vlan_allowed_for_port(self, vlan, port):
        print("mellanox: is_vlan_allowed_for_port not implemented yet")

    def remove_channel_group(self, port):
        # Remove channel-group from interface
        self.send_cmd(
            self.INTERFACE_ETHERNET % port +
            ' ' +
            self.NO_CHANNEL_GROUP)

    def add_vlans_to_port(self, port, vlans):
        # Enable hybrid mode for port
        self.send_cmd(
            self.INTERFACE_ETHERNET % port +
            ' ' +
            self.SWITCHPORT_MODE_HYBRID)

        # Add VLANs to port
        for vlan in vlans:
            self.send_cmd(
                self.INTERFACE_ETHERNET % port +
                ' ' +
                self.SWITCHPORT_HYBRID_ALLOWED_VLAN % vlan)

    def add_vlans_to_lag_port_channel(self, port, vlans):
        # Enable hybrid mode for port
        self.send_cmd(
            self.LAG_PORT_CHANNEL % port +
            ' ' +
            self.SWITCHPORT_MODE_HYBRID)

        # Add VLANs to port
        for vlan in vlans:
            self.send_cmd(
                self.LAG_PORT_CHANNEL % port +
                ' ' +
                self.SWITCHPORT_HYBRID_ALLOWED_VLAN % vlan)

    def add_vlans_to_mlag_port_channel(self, port, vlans):
        # Enable hybrid mode for port
        self.send_cmd(
            self.MLAG_PORT_CHANNEL % port +
            ' ' +
            self.SWITCHPORT_MODE_HYBRID)

        # Add VLANs to port
        for vlan in vlans:
            self.send_cmd(
                self.MLAG_PORT_CHANNEL % port +
                ' ' +
                self.SWITCHPORT_HYBRID_ALLOWED_VLAN % vlan)

    def set_mtu_for_port(self, port, mtu):
        # Bring port down
        self.send_cmd(
            self.INTERFACE_ETHERNET % port + ' ' + self.SHUTDOWN)

        # Set MTU
        self.send_cmd(
            self.INTERFACE_ETHERNET % port + ' ' + self.SET_MTU % mtu)

        # Bring port up
        self.send_cmd(
            self.INTERFACE_ETHERNET % port + ' ' + self.NO_SHUTDOWN)

    def set_mtu_for_lag_port_channel(self, port, mtu):
        # Set port-channel MTU
        self.send_cmd(
            self.LAG_PORT_CHANNEL % port +
            ' ' +
            self.SET_MTU % mtu +
            ' ' +
            self.FORCE)

    def set_mtu_for_mlag_port_channel(self, port, mtu):
        # Set port-channel MTU
        self.send_cmd(
            self.MLAG_PORT_CHANNEL % port +
            ' ' +
            self.SET_MTU % mtu +
            ' ' +
            self.FORCE)

    def create_lag(self, port_channel):
        # Create a LAG
        self.send_cmd(
            self.LAG_PORT_CHANNEL % port_channel)

    def activate_lag(self, port_channel, ports):
        # Map a physical port to the LAG in active mode (LACP)
        for port in ports:
            self.send_cmd(
                self.INTERFACE_ETHERNET % (port) +
                ' ' +
                self.LACP % port_channel)

    def enable_lacp(self):
        self.send_cmd(self.ENABLE_LACP)

    def enable_mlag(self):
        self.send_cmd(self.ENABLE_MLAG)

    def configure_mlag(self, switch_index):
        vlan = self.inv.get_mlag_vlan()
        port_channel = self.inv.get_mlag_port_channel()
        cidr_mlag_ipl = self.inv.get_cidr_mlag_ipl(switch_index)
        ipaddr_mlag_ipl_peer = self.inv.get_ipaddr_mlag_ipl_peer(switch_index)
        ipaddr_mlag_vip = self.inv.get_ipaddr_mlag_vip()

        # Enable IP routing
        self.send_cmd(self.IP_ROUTING)

        # Enable QoS
        self.send_cmd(self.QOS_ENABLE)

        # Enable MLAG protocol commands
        self.send_cmd(self.MLAG)

        # Create MLAG VLAN
        self.send_cmd(self.SET_VLAN % vlan)

        # Create a LAG
        self.send_cmd(
            self.LAG_PORT_CHANNEL % port_channel)

        # Map a physical port to the LAG in active mode (LACP)
        for port in self.inv.yield_mlag_ports(switch_index):
            self.send_cmd(
                self.INTERFACE_ETHERNET % (port) +
                ' ' +
                self.LACP % port_channel)

        # Set this LAG as an IPL
        self.send_cmd(
            self.LAG_PORT_CHANNEL % port_channel + ' ' + self.IPL)

        # Enable QoS on this specific interface
        self.send_cmd(
            self.LAG_PORT_CHANNEL % port_channel + ' ' + self.QOS_ON)

        # Create VLAN interface
        self.send_cmd(
            self.INTERFACE_VLAN % vlan)

        # Set MLAG IPL IP address
        self.send_cmd(
            self.INTERFACE_VLAN % vlan +
            ' ' +
            self.IP_CIDR % cidr_mlag_ipl)

        # Set MLAG Peer IP address
        self.send_cmd(
            self.INTERFACE_VLAN % vlan +
            ' ' +
            self.IPL +
            ' ' +
            self.PEER_ADDR % ipaddr_mlag_ipl_peer)

        # Set MLAG VIP
        self.send_cmd(
            self.MLAG_VIP % ipaddr_mlag_vip)

    def create_mlag_interface(self, port):
        # Create MLAG interface
        self.send_cmd(
            self.MLAG_PORT_CHANNEL % port)

        self.send_cmd(
            self.MLAG_PORT_CHANNEL % port + ' ' + self.STP_PORT_TYPE_EDGE)

        self.send_cmd(
            self.MLAG_PORT_CHANNEL % port + ' ' + self.STP_BPDUFILTER_ENABLE,
            'Set port %d spanning-tree bpdufilter enable' % port)

    def bind_mlag_interface(self, port):
        # Bind and enable MLAG interface
        self.send_cmd(
            self.INTERFACE_ETHERNET % port + ' ' + self.MLAG_ACTIVE % port)

        self.send_cmd(
            self.MLAG_PORT_CHANNEL % port + ' ' + self.NO_SHUTDOWN)

    def get_macs(self):
        port_to_mac = AttrDict()

        if self.mode is not 'passive':
            output = self.send_cmd(self.SHOW_MAC_ADDRESS_TABLE)
            port_to_mac = AttrDict()
            for line in output.splitlines():
                mac_search = self.MAC_RE.search(line)
                if mac_search and "/" in line:
                    macAddr = mac_search.group().lower()
                    portInfo = line.split("/")
                    if len(portInfo) == 3:
                        # port is String  type, if port = Eth1/59/4,
                        port = portInfo[1] + "/" + portInfo[2]
                    else:
                        # port is integer type,  port = Eth1/48,
                        port = portInfo[1]
                    if port in port_to_mac:
                        port_to_mac[port].append(macAddr)
                    else:
                        port_to_mac[port] = [macAddr]
        else:
            switch = PassiveSwitch(self.log, self.host)
            scripts_path = os.path.abspath(__file__)
            passive_path = (
                re.match('(.*cluster\-genesis).*', scripts_path).group(1) +
                '/passive/')
            file_path = passive_path + self.host
            port_to_mac = switch.get_port_to_mac(file_path)
        return port_to_mac

    def clear_mac_address_table(self):
        print("IN clear_mac_address_table")
        if self.mode is not 'passive':
            print(self.CLEAR_MAC_ADDRESS_TABLE)
            self.send_cmd(self.CLEAR_MAC_ADDRESS_TABLE)
        else:
            switch = PassiveSwitch(self.log, self.host)
            switch.clear_mac_address_table()


class switch(object):
    @staticmethod
    def factory(log, host=None, userid=None, password=None, mode=None, outfile=None):
        return Mellanox(log, host, userid, password, mode, outfile)
