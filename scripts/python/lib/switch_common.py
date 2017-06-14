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

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class SwitchCommon(object):
    def __init__(self, log, ip_addr, userid, password):
        self.ip_addr = ip_addr
        self.userid = userid
        self.password = password
        self.ssh_log = FILE_PATH + '/switch_ssh.log'
        self.log = log

    def is_pingable(self):
        output = subprocess.check_output(['bash', '-c', 'ping -c2 -i.5 ' + self.ip_addr])
        if '0% packet loss' in output:
            return True
        else:
            return False
