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
import os.path
import netaddr
import datetime
from enum import Enum

from lib.switch_exception import SwitchException
from lib.switch_common import SwitchCommon
from lib.genesis import gen_passive_path, gen_path


class Cisco(SwitchCommon):
    """Class for configuring and retrieving information for a Cisco
    Nexus switch.  This class developed with Cisco 5020.  Similar
    Cisco switches may work or may need some methods overridden.
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
    # ENABLE_REMOTE_CONFIG = SwitchCommon.ENABLE_REMOTE_CONFIG
    # override ENABLE_REMOTE_CONFIG as needed.
    ENABLE_REMOTE_CONFIG = 'configure terminal ; {}'
    # override as needed per switch syntax:
    # SHOW_VLANS = 'show vlan'
    # override as needed.
    SHOW_MAC_ADDRESS_TABLE = 'show mac address-table ;'
    # override as needed:
    # CREATE_VLAN = 'vlan {}'
    # override as needed:
    # DELETE_VLAN = 'no vlan {}'
    # override as needed:
    CLEAR_MAC_ADDRESS_TABLE = ('clear mac address-table dynamic')
    INTERFACE_CONFIG = 'interface ethernet {}'
    SHOW_PORT = 'show interface brief'
    ADD_VLANS_TO_PORT = (' ;switchport trunk allowed vlan add {}')
    REMOVE_VLANS_FROM_PORT = (' ;switchport trunk allowed vlan remove {}')
    SET_SWITCHPORT_MODE = (
        'interface ethernet {} ;'
        'switchport mode {} ;'
        'exit')
    SWITCHPORT_ALLOWED_VLAN_ALL_OR_NONE = (
        'interface ethernet {} ;'
        'switchport {} allowed vlan {} ;'
        'exit')
    SWITCHPORT_ADD_ALLOWED_VLAN = (
        'interface port {} ;'
        'switchport {} allowed vlan add {} ;'
        'exit')
    SWITCHPORT_SET_NATIVE_VLAN = (
        'interface port {port}'
        ' ;switchport {mode} native vlan {nvlan}'
        ' ;exit')
    SET_NATIVE_VLAN_ACCESS = (
        'interface port {} ;'
        'switchport access vlan {} ;'
        'exit')
    SET_NATIVE_VLAN_TRUNK = (
        'interface port {} ;'
        'switchport trunk allowed vlan add {} ;'
        'switchport trunk native vlan {} ;'
        'exit')
    MGMT_INTERFACE_CONFIG = 'interface ip {}'
    SET_INTERFACE_IPADDR = ' ;ip address {}'
    SET_INTERFACE_MASK = ' ;ip netmask {}'
    SET_VLAN = ' ;vlan {}'
    SHOW_IP_INTERFACE_BRIEF = 'show ip interface brief'
    SHOW_INTERFACE = 'show interface Vlan{}'
    SET_INTERFACE = ('feature interface-vlan ;'
                     'interface vlan {} ;'
                     'ip address {} {} ;'
                     'management ;'
                     'no shutdown')

    class PortMode(Enum):
        TRUNK = 'trunk'
        ACCESS = 'access'
        TRUNK_NATIVE = ''

    def __init__(self, log, host=None, userid=None,
                 password=None, mode=None, outfile=None):
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
        self.port_mode = self.PortMode
        super(Cisco, self).__init__(log, host, userid, password, mode, outfile)

    def show_ports(self, format=None):
        if self.mode == 'passive':
            return None
        ports = {}
        port_info = self.send_cmd(self.SHOW_PORT)
        if format is None:
            return port_info
        elif format == 'std':
            port_info = port_info.splitlines()
            for line in port_info:
                match = re.search(
                    r'Eth([0-9/]+)\s+(\d+)\s+\w+\s+(access|trunk)', line)
                if match:
                    # mode, avlans = self._get_port_detail(match)
                    ports[match.group(1)] = {
                        'mode': match.group(3),
                        'nvlan': match.group(2),
                        'avlans': ''}
            port_info = self.send_cmd('show interface trunk').split('Port')
            for item in port_info:
                if 'Vlans Allowed on Trunk' in item:
                    item = item.splitlines()
                    for line in item:
                        match = re.search(
                            'Eth((?:\d+/)+\d+)\s+((?:\d+[,-])*\d+)', line)
                        if match:
                            ports[match.group(1)]['avlans'] = match.group(2)
            return ports

    def remove_interface(self, vlan, host, netmask):
        """Removes an in-band management interface.
        Args:
            host (string): hostname or ipv4 address in dot decimal notation
            netmask (string): netmask in dot decimal notation
            vlan (int or string): value between 1 and 4094.
        raises:
            SwitchException if unable to remove interface
        """
        vlan = str(vlan)
        interfaces = self.show_interfaces(vlan, host, netmask, format='std')
        if interfaces[-1][0]['configured']:
            self.send_cmd('interface vlan {} ;no ip address {} {}'.format(vlan, host, netmask))
            self.send_cmd('no interface vlan {}'.format(vlan))
            interfaces = self.show_interfaces(vlan, host, netmask, format='std')
            if interfaces[-1][0]['configured']:
                self.log.info('Failed to remove interface Vlan {}.'.format(vlan))
                raise SwitchException('Failed to remove interface Vlan {}.'.format(vlan))
        else:
            if interfaces[-1][0]['found vlan']:
                self.log.info('Specified interface on vlan {} does not exist.'.format(vlan))
                raise SwitchException('Failed to remove interface Vlan {}.'.format(vlan))

    def show_interfaces(self, vlan='', host=None, netmask=None, format=None):
        """Gets from the switch a list of programmed in-band interfaces. The
        standard format consists of a list of lists. Each list entry contains
        the vlan number, the ip address, netmask and the number of the interface.
        which do not number the in-band interfaces, the last item in each list
        is set to '-'. When vlan, host and netmask are specified, the last list
        item contains 'True' or 'False' indicating whether an interface already
        exists with the specified vlan, host and netmask. For switches which do
        number the interfaces, (ie Lenovo) the last list item also contains the
        next available interface number and the number of the found interface.
        Args:
            vlan (string): String representation of integer between
                1 and 4094. If none specified, usually the default vlan is used.
            host (string): hostname or ipv4 address in dot decimal notation
            netmask (string): netmask in dot decimal notation
            format (string): 'std' If format is not specified, The native (raw)
                format is returned. If format is set to 'std', a 'standard' format
                is returned.
        Returns:
        If format is unspecified, returns a raw string of data as it
        comes from the switch. If format == 'std' a standard format is returned.
        Standard format consists of a list of lists. Each list entry contains
        the vlan number, the ip address, netmask and the number of the interface.
        For switches which do not number the in-band interfaces, the last item
        in each list is set to '-'. When vlan, host and netmask are specified,
        the last list item contains a dictionary. The dictionary has three entries;
            'configured' : set to True or False indicating whether an
                interface already exists with the specified vlan, host and netmask.
            'avail ifc' : For switches which do number the interfaces, (ie Lenovo)
                this dictioanary entry contains the next available interface number.
            'found ifc' : For switches which do number the interfaces, this entry
                contains the number of the found interface.
        """
        if self.mode == 'passive':
            return None
        ifcs = []
        ifc_info = ''
        vlan = str(vlan)
        found, found_vlan = False, False
        ifc_info_brief = self.send_cmd(self.SHOW_IP_INTERFACE_BRIEF)
        vlan_ifcs = re.findall(r'Vlan(\d+)', ifc_info_brief, re.MULTILINE)
        for ifc in vlan_ifcs:
            ifc_info = ifc_info + self.send_cmd(self.SHOW_INTERFACE.format(ifc))
        if format is None:
            return ifc_info
        ifc_info = ifc_info.split('Vlan')
        for line in ifc_info:
            match = re.search(r'(\d+).*Internet Address is\s+'
                              '((\w+.\w+.\w+.\w+)/\d+)', line, re.DOTALL)
            if match:
                mask = netaddr.IPNetwork(match.group(2))
                mask = str(mask.netmask)
                ifcs.append(
                    [match.group(1), match.group(3), mask, '-'])
                if (vlan, host, netmask, '-') == tuple(ifcs[-1]):
                    found = True
                if vlan in ifcs[-1]:
                    found_vlan = True
        ifcs.append([{'configured': found, 'found vlan': found_vlan}])
        return ifcs

    def configure_interface(self, host, netmask, vlan=1, intf=None):
        """Configures a management interface. This implementation checks
        if the host ip is already in use. If it is, a check is made to
        see if it is configured as specified. If not, an exception is raised.
        Lenovo numbers interfaces. The specified vlan will be created if it
        does not already exist.

        When implementing this method for a new switch, minimally this method
        should configure (overwrite if necessary) the specified interface.

        Args:
            host (string): hostname or ipv4 address in dot decimal notation
            netmask (string): netmask in dot decimal notation
            vlan (string): String representation of integer between
            1 and 4094. The management interface is created on the specified
            vlan intf (string): optional. String representation of integer
            between 1 and 128.
        raises:
            SwitchException if unable to program interface
        """
        vlan = str(vlan)
        interfaces = self.show_interfaces(vlan, host, netmask, format='std')
        if interfaces[-1][0]['configured']:
            self.log.info(
                'Switch interface vlan {} already configured'.format(vlan))
            return
        if interfaces[-1][0]['found vlan']:
            self.log.info(
                'Conflicting address. Interface vlan {} already configured'.format(vlan))
            raise SwitchException(
                'Conflicting address exists on interface vlan {}'.format(vlan))
            return
        # create vlan if it does not already exist
        self.create_vlan(vlan)

        # create the interface

        self.send_cmd(self.SET_INTERFACE.format(vlan, host, netmask))
        interfaces = self.show_interfaces(vlan, host, netmask, format='std')
        if not interfaces[-1][0]['configured']:
            raise SwitchException(
                'Failed configuring management interface vlan {}'.format(vlan))


class switch(object):
    @staticmethod
    def factory(log, host=None, userid=None, password=None, mode=None, outfile=None):
        return Cisco(log, host, userid, password, mode, outfile)
