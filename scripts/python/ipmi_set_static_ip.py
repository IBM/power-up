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
import re
from pyghmi.ipmi import command as ipmi_command
from pyghmi import exceptions as pyghmi_exception

from lib.inventory import Inventory
from lib.logger import Logger

STATIC = 'Static'
DHCP_ERR_MSG = 'IPMI IP is already \'%s\' - Rack: %s - IP: %s - MAC: %s'
IPV4_ERR_MSG = ('IPMI and inventory file IP differ'
                ' - Rack: %s - IP(IPMI/INV): %s/%s - MAC: %s')
IPMI_GET_ERR_MSG = 'IPMI LAN query failed - Rack: %s - IP: %s - Error: %s'
IPMI_SET_ERR_MSG = ('IPMI IP change to \'%s\' failed'
                    ' - Rack: %s - IP: %s - MAC: %s - Error: %s')
IPMI_SET_MSG = 'IPMI IP changed to \'%s\' - Rack: %s - IP: %s - MAC: %s'


class IpmiSetStaticIP(object):
    def __init__(self, log_level, inv_file):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        inv = Inventory(log_level, inv_file)
        for rack_id, ipv4, _userid, _password in inv.yield_ipmi_access_info():
            ipmi_cmd = ipmi_command.Command(
                bmc=ipv4,
                userid=_userid,
                password=_password)

            try:
                inv = ipmi_cmd.get_net_configuration(
                    channel=None, gateway_macs=False)
            except pyghmi_exception.IpmiException as error:
                log.error(
                    IPMI_GET_ERR_MSG %
                    (rack_id, ipv4, str(error)))
                sys.exit(1)

            m = re.search('^(.+?)/', inv['ipv4_address'])
            inv_ipv4_address_no_mask = m.group(1)

            # Check that IPMI port is not set to Static
            if inv['ipv4_configuration'] == STATIC:
                try:
                    raise Exception()
                except:
                    log.error(
                        DHCP_ERR_MSG %
                        (
                            STATIC,
                            rack_id,
                            inv_ipv4_address_no_mask,
                            inv['mac_address']))
                    sys.exit(1)

            # Compare ipv4 address on IPMI port versus inventory file
            if inv_ipv4_address_no_mask != ipv4:
                try:
                    raise Exception()
                except:
                    log.error(
                        IPV4_ERR_MSG %
                        (
                            rack_id,
                            inv_ipv4_address_no_mask,
                            ipv4,
                            inv['mac_address']))
                    sys.exit(1)

            # Compare mac address on IPMI port versus inventory file

            try:
                ipmi_cmd.set_net_configuration(
                    ipv4_address=inv['ipv4_address'],
                    ipv4_configuration='Static',
                    ipv4_gateway=inv['ipv4_gateway'],
                    channel=None)
                log.info(
                    IPMI_SET_MSG %
                    (STATIC, rack_id, ipv4, inv['mac_address']))
            except pyghmi_exception.IpmiException as error:
                log.error(
                    IPMI_SET_ERR_MSG %
                    (STATIC, rack_id, ipv4, inv['mac_address'], str(error)))
                sys.exit(1)


if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: log level
    """
    log = Logger(__file__)

    ARGV_MAX = 3
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            sys.exit(1)

    log.clear()

    inv_file = sys.argv[1]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[2]
    else:
        log_level = None
    IpmiSetStaticIP(log_level, inv_file)
