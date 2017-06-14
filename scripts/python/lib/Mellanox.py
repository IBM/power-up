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

from lib.ssh import SSH, SSH_CONNECTION
import switch_common


class Mellanox(switch_common.SwitchCommon):
    def __init__(self, log, ip_addr, userid, password):
        switch_common.SwitchCommon.__init__(self, log, ip_addr, userid, password)
        self.CLI_ENABLE = 'cli enable %s'
        self.ENABLE_REMOTE_CONFIG = 'cli enable \"configure terminal\" %s'

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
        ssh = SSH_CONNECTION(
            self.ip_addr,
            ssh_log=self.ssh_log,
            username=self.userid,
            password=self.password,
            look_for_keys=False)

        cmd = self.CLI_ENABLE % '\"show vlan\"'
        _, vlan_info, _ = ssh.send_cmd(cmd)
        ssh.close()
        return vlan_info

    def show_mac_address_table(self):
        cmd = self.CLI_ENABLE % '\"show mac-address-table\"'
        mac_info = self.send_cmd(cmd)
        return mac_info


class switch(object):
    @staticmethod
    def factory(log, ip_addr, userid, password):
        return Mellanox(log, ip_addr, userid, password)
