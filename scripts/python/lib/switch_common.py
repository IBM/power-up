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

from lib.ssh import SSH

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class SwitchCommon(object):
    def __init__(self, log, ip_addr=None, userid=None, password=None, mode=None, outfile=None):
        pass

    def is_pingable(self):
        if self.mode == 'passive':
            return None
        output = subprocess.check_output(['bash', '-c', 'ping -c2 -i.5 ' + self.ip_addr])
        if '0% packet loss' in output:
            return True
        else:
            return False

    def send_cmd(self, cmd):
        if self.mode == 'passive':
            f = open(self.outfile, 'a+')
            f.write(cmd)
            f.close()
            return
        ssh = SSH(self.log)
        __, data, _ = ssh.exec_cmd(
            self.ip_addr,
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
            dictionary: Keys are integer port numbers and values are a list
            of MAC addresses.
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
                q = re.findall(r'[\w+:*\.*/*\w*]+', line)
                port = q[port_col]
                if port not in mac_dict.keys():
                    mac_dict[port] = [match.group()]
                else:
                    mac_dict[port].append(match.group())
        return mac_dict
