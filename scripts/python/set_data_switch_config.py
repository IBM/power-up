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
import os.path

from lib.inventory import Inventory
from lib.logger import Logger
from lib.ssh import SSH
from write_switch_memory import WriteSwitchMemory

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class ConfigureDataSwitch(object):
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

    def __init__(self, log, inv_file):
        self.inv = Inventory(log, inv_file)
        self.log = log

        for self.ipv4, self.userid, self.password, vlans \
                in self.inv.yield_data_vlans():
            for vlan in vlans:
                self._send_cmd(self.SET_VLAN % vlan, 'Create vlan %s' % vlan)

        switch_index = 0
        for self.ipv4, self.userid, self.password, port_vlans, port_mtu, \
                port_bonds in self.inv.yield_data_switch_ports():
            if port_bonds:
                for ports in port_bonds.values():
                    for port in ports:
                        # Set port mode and add VLANs
                        if port in port_vlans:
                            self._add_vlans_to_port(port, port_vlans[port])
                        # Specify MTU
                        if port in port_mtu:
                            self._set_mtu_for_port(port, port_mtu[port])
            else:
                for port, vlans in port_vlans.items():
                    # Set port mode and add VLANs
                    self._add_vlans_to_port(port, vlans)
                for port, mtu in port_mtu.items():
                    # Specify MTU
                    self._set_mtu_for_port(port, mtu)

            if port_bonds:
                # Enable LACP
                self._enable_lacp()
                # Configure port for MLAG
                if self.inv.is_mlag():
                    self._configure_mlag(switch_index)
                    for port_channel, ports in port_bonds.items():
                        # Remove any channel-group from port
                        self._remove_channel_group(ports[0])
                        self._create_mlag_interface(port_channel)
                        if ports[0] in port_vlans:
                            self._add_vlans_to_mlag_port_channel(
                                port_channel, port_vlans[ports[0]])
                        if ports[0] in port_mtu:
                            self._set_mtu_for_mlag_port_channel(
                                port_channel, port_mtu[ports[0]])
                        self._bind_mlag_interface(port_channel)
                    # Enable MLAG
                    self._send_cmd(self.ENABLE_MLAG, 'Enable MLAG')
                # Configure port for LAG
                else:
                    for port_channel, ports in port_bonds.items():
                        for port in ports:
                            self._remove_channel_group(port)
                        if ports[0] in port_vlans:
                            self._add_vlans_to_lag_port_channel(
                                port_channel, port_vlans[ports[0]])
                        if ports[0] in port_mtu:
                            self._set_mtu_for_lag_port_channel(
                                port_channel, port_mtu[ports[0]])
                        self._create_lag(port_channel)
                        self._activate_lag(port_channel, ports)

            switch_index += 1

        if self.inv.is_write_switch_memory():
            switch = WriteSwitchMemory(LOG, INV_FILE)
            switch.write_data_switch_memory()

    def _remove_channel_group(self, port):
        # Remove channel-group from interface
        self._send_cmd(
            self.INTERFACE_ETHERNET % port +
            ' ' +
            self.NO_CHANNEL_GROUP,
            'Remove channel-group for port %s' % port,
            False)

    def _add_vlans_to_port(self, port, vlans):
        # Enable hybrid mode for port
        self._send_cmd(
            self.INTERFACE_ETHERNET % port +
            ' ' +
            self.SWITCHPORT_MODE_HYBRID,
            'Enable hybrid mode for port %s' % port)

        # Add VLANs to port
        for vlan in vlans:
            self._send_cmd(
                self.INTERFACE_ETHERNET % port +
                ' ' +
                self.SWITCHPORT_HYBRID_ALLOWED_VLAN % vlan,
                'Add vlan %s to port %s in hybrid mode' % (vlan, port))

    def _add_vlans_to_lag_port_channel(self, port, vlans):
        # Enable hybrid mode for port
        self._send_cmd(
            self.LAG_PORT_CHANNEL % port +
            ' ' +
            self.SWITCHPORT_MODE_HYBRID,
            'Enable hybrid mode for LAG port-channel %s' % port)

        # Add VLANs to port
        for vlan in vlans:
            self._send_cmd(
                self.LAG_PORT_CHANNEL % port +
                ' ' +
                self.SWITCHPORT_HYBRID_ALLOWED_VLAN % vlan,
                ('Add vlan %d to LAG port-channel %d'
                 ' in hybrid mode') % (vlan, port))

    def _add_vlans_to_mlag_port_channel(self, port, vlans):
        # Enable hybrid mode for port
        self._send_cmd(
            self.MLAG_PORT_CHANNEL % port +
            ' ' +
            self.SWITCHPORT_MODE_HYBRID,
            'Enable hybrid mode for MLAG port-channel %s' % port)

        # Add VLANs to port
        for vlan in vlans:
            self._send_cmd(
                self.MLAG_PORT_CHANNEL % port +
                ' ' +
                self.SWITCHPORT_HYBRID_ALLOWED_VLAN % vlan,
                ('Add vlan %d to MLAG port-channel %d'
                 ' in hybrid mode') % (vlan, port))

    def _set_mtu_for_port(self, port, mtu):
        # Bring port down
        self._send_cmd(
            self.INTERFACE_ETHERNET % port + ' ' + self.SHUTDOWN,
            'Shut down port %s' % port)

        # Set MTU
        self._send_cmd(
            self.INTERFACE_ETHERNET % port + ' ' + self.SET_MTU % mtu,
            'Set port %s mtu to %s' % (port, mtu))

        # Bring port up
        self._send_cmd(
            self.INTERFACE_ETHERNET % port + ' ' + self.NO_SHUTDOWN,
            'Bring up port %s' % port)

    def _set_mtu_for_lag_port_channel(self, port, mtu):
        # Set port-channel MTU
        self._send_cmd(
            self.LAG_PORT_CHANNEL % port +
            ' ' +
            self.SET_MTU % mtu +
            ' ' +
            self.FORCE,
            'Set LAG port-channel %d mtu to %d' % (port, mtu))

    def _set_mtu_for_mlag_port_channel(self, port, mtu):
        # Set port-channel MTU
        self._send_cmd(
            self.MLAG_PORT_CHANNEL % port +
            ' ' +
            self.SET_MTU % mtu +
            ' ' +
            self.FORCE,
            'Set MLAG port-channel %d mtu to %d' % (port, mtu))

    def _create_lag(self, port_channel):
        # Create a LAG
        self._send_cmd(
            self.LAG_PORT_CHANNEL % port_channel,
            'Create LAG port-channel %d' % port_channel)

    def _activate_lag(self, port_channel, ports):
        # Map a physical port to the LAG in active mode (LACP)
        for port in ports:
            self._send_cmd(
                self.INTERFACE_ETHERNET % (port) +
                ' ' +
                self.LACP % port_channel,
                'Map port %s to LAG port-channel %d' %
                (port, port_channel))

    def _enable_lacp(self):
        self._send_cmd(self.ENABLE_LACP, 'Enable LACP')

    def _configure_mlag(self, switch_index):
        vlan = self.inv.get_mlag_vlan()
        port_channel = self.inv.get_mlag_port_channel()
        cidr_mlag_ipl = self.inv.get_cidr_mlag_ipl(switch_index)
        ipaddr_mlag_ipl_peer = self.inv.get_ipaddr_mlag_ipl_peer(switch_index)
        ipaddr_mlag_vip = self.inv.get_ipaddr_mlag_vip()

        # Enable IP routing
        self._send_cmd(self.IP_ROUTING, 'Enable IP routing')

        # Enable QoS
        self._send_cmd(self.QOS_ENABLE, 'Enable QoS')

        # Enable MLAG protocol commands
        self._send_cmd(self.MLAG, 'Enable MLAG protocol commands')

        # Create MLAG VLAN
        self._send_cmd(self.SET_VLAN % vlan, 'Create MLAG VLAN %d' % vlan)

        # Create a LAG
        self._send_cmd(
            self.LAG_PORT_CHANNEL % port_channel,
            'Create LAG port-channel %d' % port_channel)

        # Map a physical port to the LAG in active mode (LACP)
        for port in self.inv.yield_mlag_ports(switch_index):
            self._send_cmd(
                self.INTERFACE_ETHERNET % (port) +
                ' ' +
                self.LACP % port_channel,
                'Map port %s to LAG port-channel %d' % (port, port_channel))

        # Set this LAG as an IPL
        self._send_cmd(
            self.LAG_PORT_CHANNEL % port_channel + ' ' + self.IPL,
            'Set LAG port-channel %d as an IPL' % port_channel)

        # Enable QoS on this specific interface
        self._send_cmd(
            self.LAG_PORT_CHANNEL % port_channel + ' ' + self.QOS_ON,
            'Enable QoS port-channel %d' % port_channel)

        # Create VLAN interface
        self._send_cmd(
            self.INTERFACE_VLAN % vlan, 'Create VLAN %d interface' % vlan)

        # Set MLAG IPL IP address
        self._send_cmd(
            self.INTERFACE_VLAN % vlan +
            ' ' +
            self.IP_CIDR % cidr_mlag_ipl,
            'Set MLAG IPL CIDR \'%s\' with VLAN %d' % (cidr_mlag_ipl, vlan))

        # Set MLAG Peer IP address
        self._send_cmd(
            self.INTERFACE_VLAN % vlan +
            ' ' +
            self.IPL +
            ' ' +
            self.PEER_ADDR % ipaddr_mlag_ipl_peer,
            'Set MLAG IPL peer-address %s with VLAN %d' %
            (ipaddr_mlag_ipl_peer, vlan))

        # Set MLAG VIP
        self._send_cmd(
            self.MLAG_VIP % ipaddr_mlag_vip,
            'Set MLAG VIP CIDR \'%s\'' % ipaddr_mlag_vip)

    def _create_mlag_interface(self, port):
        # Create MLAG interface
        self._send_cmd(
            self.MLAG_PORT_CHANNEL % port,
            'Create MLAG interface %d' % port)

        self._send_cmd(
            self.MLAG_PORT_CHANNEL % port + ' ' + self.STP_PORT_TYPE_EDGE,
            'Set port %d spanning-tree port type edge' % port)

        self._send_cmd(
            self.MLAG_PORT_CHANNEL % port + ' ' + self.STP_BPDUFILTER_ENABLE,
            'Set port %d spanning-tree bpdufilter enable' % port)

    def _bind_mlag_interface(self, port):
        # Bind and enable MLAG interface
        self._send_cmd(
            self.INTERFACE_ETHERNET % port + ' ' + self.MLAG_ACTIVE % port,
            'Bind port %d to the MLAG group %d' % (port, port))

        self._send_cmd(
            self.MLAG_PORT_CHANNEL % port + ' ' + self.NO_SHUTDOWN,
            'Enable the MLAG interface %d' % port)

    def _send_cmd(self, cmd, msg, status_check=True):
        ssh = SSH(self.log)
        self.log.debug(cmd)
        status, stdout_, _ = ssh.exec_cmd(
            self.ipv4,
            self.userid,
            self.password,
            self.ENABLE_REMOTE_CONFIG % cmd)
        if status:
            if status_check:
                self.log.error(
                    'Failed: ' + msg + ' on ' + self.ipv4 +
                    ' - Error: ' +
                    stdout_.replace('\n', ' ').replace('\r', ''))
                exit(1)
            else:
                self.log.info(
                    msg + ' on ' + self.ipv4 +
                    ' - Error: ' +
                    stdout_.replace('\n', ' ').replace('\r', ''))
        else:
            self.log.info(msg + ' on ' + self.ipv4)


if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: log level
    """
    LOG = Logger(__file__)

    if len(sys.argv) != 3:
        try:
            raise Exception()
        except:
            LOG.error('Invalid argument count')
            sys.exit(1)

    INV_FILE = sys.argv[1]
    LOG.set_level(sys.argv[2])

    ConfigureDataSwitch(LOG, INV_FILE)
