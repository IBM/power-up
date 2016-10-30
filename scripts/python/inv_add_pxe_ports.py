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

from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals
import sys
import os.path
from orderedattrdict import AttrDict

from lib.inventory import Inventory
from lib.logger import Logger
from get_mgmt_switch_config import GetMgmtSwitchConfig
from get_dhcp_lease_info import GetDhcpLeases


class InventoryAddPxe(object):
    def __init__(self, dhcp_leases_file, log_level, inv_file):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        dhcp_leases = GetDhcpLeases(dhcp_leases_file, log_level)
        dhcp_mac_ip = dhcp_leases.get_mac_ip()

        inv = Inventory(log_level, inv_file)
        mgmt_switch_config = GetMgmtSwitchConfig(log_level)
        mgmt_sw_cfg = AttrDict()
        for rack, ipv4 in inv.yield_mgmt_rack_ipv4():
            mgmt_sw_cfg[rack] = mgmt_switch_config.get_port_mac(rack, ipv4)

        inv.add_pxe(dhcp_mac_ip, mgmt_sw_cfg)

        for rack, mac, ip in inv.yield_node_pxe():
            log.info(
                'PXE node detected - Rack: %s - MAC: %s - IP: %s' %
                (rack, mac, ip))

if __name__ == '__main__':
    """
    Arg1: config file
    Arg2: inventory file
    Arg3: DHCP leases file
    Arg4: log level
    """
    log = Logger(__file__)

    ARGV_MAX = 5
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    inv_file = sys.argv[1]
    dhcp_leases_file = sys.argv[2]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[3]
    else:
        log_level = None

    ipmi_data = InventoryAddPxe(
        dhcp_leases_file, log_level, inv_file)
