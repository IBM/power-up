#!/usr/bin/env python
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

import os.path
import paramiko
import re

from lib.logger import Logger

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

SHOW_MACS_CMD = '\"show mac-address-table\"'
CLEAR_MACS_CMD = '\"clear mac-address-table dynamic\"'
MAC_RE = re.compile('([\da-fA-F]{2}:){5}([\da-fA-F]{2})')


class MellanoxSwitch(object):
    def __init__(self, log_level):
        self.SWITCH_PORT = 22

        self.DEBUG = b'DEBUG'
        self.INFO = b'INFO'
        self.SSH_LOG = 'leaf-switch-ssh.log'

        self.ENABLE_REMOTE_CONFIG = 'cli enable \"configure terminal\" %s'

        self.log = Logger(__file__)
        self.log_level = log_level
        if log_level is not None:
            self.log.set_level(log_level)

    def get_macs(self, inv):
        switch_ip_to_mac_map = {}
        for switch_ip, creds in inv.get_data_switches().iteritems():
            output = self.issue_cmd(SHOW_MACS_CMD, switch_ip, creds['user'],
                                    creds['password'])
            port_to_mac = {}
            for line in output.splitlines():
                mac_search = MAC_RE.search(line)
                if mac_search:
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
            switch_ip_to_mac_map[switch_ip] = port_to_mac
        return switch_ip_to_mac_map

    def clear_mac_address_table(self, inv):
        for switch_ip, creds in inv.get_data_switches().iteritems():
            self.issue_cmd(CLEAR_MACS_CMD, switch_ip, creds['user'],
                           creds['password'])

    def issue_cmd(self, cmd, ip, userid, pwd):
        if self.log_level == self.DEBUG or self.log_level == self.INFO:
            paramiko.util.log_to_file(self.SSH_LOG)
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(ip, self.SWITCH_PORT, userid, pwd)
        stdin, stdout, stderr = s.exec_command(
            self.ENABLE_REMOTE_CONFIG % (cmd))
        output = stdout.read()
        s.close()
        return output
