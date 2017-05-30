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
import re
from orderedattrdict import AttrDict


class GetDhcpLeases(object):
    def __init__(self, dhcp_leases_file, log):
        dhcp_leases_file = os.path.abspath(
            os.path.dirname(os.path.abspath(dhcp_leases_file)) +
            os.path.sep +
            os.path.basename(dhcp_leases_file))

        try:
            fds = open(dhcp_leases_file, 'r')
        except:
            log.error('DHCP leases file not found: %s' % (dhcp_leases_file))
            sys.exit(1)
        self.mac_ip = AttrDict()
        for line in fds:
            match = re.search(
                r'^\S+\s+(\S+)\s+(\S+)',
                line)
            mac = match.group(1)
            ipaddr = match.group(2)
            self.mac_ip[mac] = ipaddr
            log.info('Lease found - MAC: %s - IP: %s' % (mac, ipaddr))

    def get_mac_ip(self):
        return self.mac_ip
