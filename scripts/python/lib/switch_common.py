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

import os.path
import subprocess
import re
from orderedattrdict import AttrDict

from lib.ssh import SSH
from lib.switch_exception import SwitchException

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class SwitchCommon(object):
    ENABLE_REMOTE_CONFIG = 'enable;configure terminal; %s'
    SHOW_VLANS = 'show vlan'
    CREATE_VLAN = 'vlan {}'
    DELETE_VLAN = 'no vlan {}'
    CLEAR_MAC_ADDRESS_TABLE = 'clear mac-address-table'
    SHOW_MAC_ADDRESS_TABLE = 'show mac-address-table'
    SHOW_INTERFACE = 'show interface ip {}'

    def __init__(self, log, host=None, userid=None, password=None, mode=None, outfile=None):
        pass

    def show_vlans(self):
        if self.mode == 'passive':
            return None
        vlan_info = self.send_cmd(self.SHOW_VLANS)
        return vlan_info

    def create_vlan(self, vlan):
        if self.mode == 'passive':
            return
        self.send_cmd(self.CREATE_VLAN.format(vlan))
        if self.is_vlan_created(vlan):
            self.log.info(
                'Created VLAN {}'.format(vlan))
        else:
            raise SwitchException(
                'Failed creating VLAN {}'.format(vlan))

    def delete_vlan(self, vlan):
        if self.mode == 'passive':
            return
        self.send_cmd(self.DELETE_VLAN.format(vlan))
        if self.is_vlan_created(vlan):
            self.log.warning(
                'Failed deleting VLAN {}'.format(vlan))
            raise SwitchException(
                'Failed deleting VLAN {}'.format(vlan))
        self.log.info('vlan {} deleted.'.format(vlan))
        return

    def is_vlan_created(self, vlan):
        if self.mode == 'passive':
            return None
        if re.search(
                r'^' + str(vlan),
                self.send_cmd(self.SHOW_VLANS),
                re.MULTILINE):
            return True
        return False

    def show_interfaces(self, vlan=''):
        ifc_info = self.send_cmd(self.SHOW_INTERFACE.format(vlan))
        return ifc_info

    def show_mac_address_table(self, format=False):
        """Get switch mac address table.

        The returned text string can be raw or optionally fomatted.

        Args:
            format (boolean) : set to 'dict' or 'std' to return a dictionary
        Returns:
            raw string if format=False
            dictionary of ports and mac address values in native switch form
            if format = 'dict'.
            ordered dictionary of ports and mac address values in a standard
            format if fmt = 'std'.
        """
        if self.mode == 'passive':
            mac_info = {}
            try:
                with open(self.host, 'r') as f:
                    mac_info = f.read()

            except IOError as error:
                self.log.error(
                    'Passive switch MAC address table file not found (%s)' % error)
                raise
            mac_info = self.get_port_to_mac(mac_info, self.log)
            return mac_info

        mac_info = self.send_cmd(self.SHOW_MAC_ADDRESS_TABLE)
        if not format:
            return mac_info
        if format == 'dict':
            return self.get_mac_dict(mac_info)
        if format == 'std':
            return self.get_port_to_mac(mac_info, self.log)

    def clear_mac_address_table(self):
        if self.mode == 'passive':
            return
        self.send_cmd(self.CLEAR_MAC_ADDRESS_TABLE)

    def is_pingable(self):
        try:
            if self.mode == 'passive':
                return None
            output = subprocess.check_output(['bash', '-c', 'ping -c2 -i.5 ' + self.host])
            if '0% packet loss' in output:
                return True
            else:
                return False
        except subprocess.CalledProcessError as exc:
            self.log.error('Unable to ping switch.  {}'.format(exc))
            return False

    def send_cmd(self, cmd):
        if self.mode == 'passive':
            f = open(self.outfile, 'a+')
            f.write(cmd + '\n')
            f.close()
            return

        if self.ENABLE_REMOTE_CONFIG:
            cmd = self.ENABLE_REMOTE_CONFIG % (cmd)

        ssh = SSH(self.log)
        __, data, _ = ssh.exec_cmd(
            self.host,
            self.userid,
            self.password,
            cmd,
            ssh_log=FILE_PATH + '/switch_ssh.log',
            look_for_keys=False)
        return data

    @staticmethod
    def get_mac_dict(mac_address_table):
        """Convert MAC address table to dictionary.

        Args:
            mac_address_table (string): MAC address table. Lines delimited
            with line feed.  Assumes a header row with "Port" as a column
            header followed by a delimiter row composed of dashes ('-')
            which delimit columns.  Handles MAC addresses formatted
            as 'cc:cc:cc:cc:cc:cc' or 'cccc.cccc.cccc'

        Returns:
            dictionary: Keys are string port numbers and values are a list
            of MAC addresses both in native switch format.
        """
        port_col = None
        pos = None
        mac_dict = {}
        p = re.compile(r'\w+\.\w+\.\w+|\w+:\w+:\w+:\w+:\w+:\w+')
        mac_address_table = mac_address_table.splitlines()
        p2 = re.compile('Port', re.IGNORECASE)
        for line in mac_address_table:
            # find row with 'Port' label
            match = p2.search(line)
            if match:
                pos = match.start()
            # find header seperator row
            if re.search('-+', line):
                iter = re.finditer('-+', line)
                i = 0
                for match in iter:
                    # find column aligned with 'Port'
                    if pos >= match.span()[0] and pos < match.span()[1]:
                        port_col = i
                    i += 1
            # find rows with MACs
            match = p.search(line)
            if match:
                # isolate columns, extract row with macs
                q = re.findall(r'[\w+:./]+', line)
                port = q[port_col]
                if port not in mac_dict.keys():
                    mac_dict[port] = [match.group()]
                else:
                    mac_dict[port].append(match.group())
        return mac_dict

    @staticmethod
    def get_port_to_mac(mac_address_table, log=None):
        """Get Attribute Dictionary mapping ports to lists of MAC address.

        The returned attribute dictionary provides port numbers mapped to lists
        of MAC addresses (from the switch MAC address table). Individual ports
        can easily be retrieved by using the port number as the dictionary key.

        Args:
            mac_address_table_ (string):  MAC address table with rows delimited
            by linefeed.

        Returns:
            AttrDict: Port to MAC address mapping.
        """
        _mac_iee802 = '([\dA-F]{2}[\.:-]){5}([\dA-F]{2})'
        _mac_cisco = '([\dA-F]{4}\.){2}[\dA-F]{4}'
        _mac_all = "%s|%s" % (_mac_iee802, _mac_cisco)
        _mac_regex = re.compile(_mac_all, re.I)
        port_to_mac = AttrDict()
        mac_line_list = []
        port_index = None
        mac_index = None

        mac_header_re = re.compile('mac address', re.I)
        single_s = re.compile('(\S)\s(\S)')

        mac_lines = mac_address_table.splitlines()
        if log:
            log.info('Converting MAC address table with %d lines to standard dictionary format' % len(mac_lines))
        for line in mac_lines:
            if _mac_regex.search(line):
                if log:
                    log.debug('Found mac address: %s' % line.rstrip())
                mac_line_list.append(line.split())
            elif mac_header_re.search(line):
                if log:
                    log.debug('Found possible header: %s' % line.rstrip())
                header = single_s.sub('\g<1>\g<2>', line.lower()).split()
                if set(["macaddress", "port"]) <= set(header):
                    if log:
                        log.debug('header: %s' % header)
                    mac_index = header.index("macaddress")
                    port_index = header.index("port")

        if mac_index is None and mac_line_list:
            for index, value in enumerate(mac_line_list[0]):
                if _mac_regex.search(value):
                    mac_index = index

        if port_index is None and mac_line_list:
            if mac_index == 1:
                port_index = 0
            else:
                port_index = 1

        for line in mac_line_list:
            mac = line[mac_index].lower()
            mac = mac.replace("-", ":")
            mac = mac.replace(".", ":")
            for i in [2, 5, 8, 11, 14]:
                if mac[i] != ":":
                    mac = mac[:i] + ":" + mac[i:]

            if "/" in line[port_index]:
                port = line[port_index].split("/", 1)[1]
            else:
                port = line[port_index]

            if port in port_to_mac:
                port_to_mac[port].append(mac)
            else:
                port_to_mac[port] = [mac]
            if log:
                log.debug(
                    'port_to_mac[%s] = %s' % (port, port_to_mac[port]))
        if log:
            return port_to_mac
