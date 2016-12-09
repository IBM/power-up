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
import time
import netaddr
import xmlrpclib
from pyghmi.ipmi import command as ipmi_command
from pyghmi import exceptions as pyghmi_exception

from lib.inventory import Inventory
from lib.logger import Logger

COBBLER_USER = 'cobbler'
COBBLER_PASS = 'cobbler'
DNSMASQ_TEMPLATE = '/etc/cobbler/dnsmasq.template'

WAIT = True
OFF = 'off'
POWERSTATE = 'powerstate'

INV_IPV4_IPMI = 'ipv4-ipmi'
INV_IPV4_PXE = 'ipv4-pxe'
INV_MAC_IPMI = 'mac-ipmi'
INV_MAC_PXE = 'mac-pxe'
INV_RACK_ID = 'rack-id'
INV_HOSTNAME = 'hostname'


class InventoryModifyIPv4(object):
    def __init__(self, log_level, inv_file, node_mgmt_ipv4_start):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        inv_original = Inventory(log_level, inv_file)
        inv = Inventory(log_level, inv_file)

        new_ip = netaddr.IPNetwork(node_mgmt_ipv4_start)
        i = 0

        dnsmasq_template = open(DNSMASQ_TEMPLATE, 'a')
        dnsmasq_template.write('\n')

        for inventory, INV_NODES, key, index, node in inv.yield_nodes():

            log.info(
                'Logging Inventory IP   - Rack: %s - Node: %s - Key: %s '
                '- IP:     %s' %
                (node[INV_RACK_ID], node[INV_HOSTNAME], INV_IPV4_IPMI,
                 node[INV_IPV4_IPMI]))

            inv.add_to_node(key, index, INV_IPV4_IPMI, str(new_ip.ip + i))

            log.info(
                'Modifying Inventory IP - Rack: %s - Node: %s - Key: %s '
                '- New IP: %s' %
                (node[INV_RACK_ID], node[INV_HOSTNAME], INV_IPV4_IPMI,
                 node[INV_IPV4_IPMI]))

            dnsmasq_template.write(
                'dhcp-host=%s,%s-bmc,%s\n' %
                (node[INV_MAC_IPMI], node[INV_HOSTNAME], node[INV_IPV4_IPMI]))

            i += 1

            log.info(
                'Logging Inventory IP   - Rack: %s - Node: %s - Key: %s  '
                '- IP:     %s' %
                (node[INV_RACK_ID], node[INV_HOSTNAME], INV_IPV4_PXE,
                 node[INV_IPV4_PXE]))

            inv.add_to_node(key, index, INV_IPV4_PXE, str(new_ip.ip + i))

            log.info(
                'Modifying Inventory IP - Rack: %s - Node: %s - Key: %s  '
                '- New IP: %s' %
                (node[INV_RACK_ID], node[INV_HOSTNAME], INV_IPV4_PXE,
                 node[INV_IPV4_PXE]))

            i += 1

        dnsmasq_template.write('\n')
        dnsmasq_template.close()

        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)
        cobbler_server.sync(token)
        log.info("Running Cobbler sync")

        for (rack, ip, user, passwd) in inv_original.yield_ipmi_access_info():
            ipmi_cmd = ipmi_command.Command(
                bmc=ip,
                userid=user,
                password=passwd)

            rc = ipmi_cmd.reset_bmc()

            log.info(
                'BMC Cold Reset Issued - Rack: %s - IP: %s' %
                (rack, ip))

        time.sleep(120)

        for rack_id, ipv4, _userid, _password in inv.yield_ipmi_access_info():
            ipmi_cmd = ipmi_command.Command(
                bmc=ipv4,
                userid=_userid,
                password=_password)

            try:
                rc = ipmi_cmd.get_power()
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'BMC Power status failed - Rack: %s - IP: %s, %s' %
                    (rack_id, ipv4, str(error)))
                sys.exit(1)

            if rc.get(POWERSTATE) == OFF:
                log.info(
                    'BMC at Standby - Rack: %s - IP: %s' %
                    (rack_id, ipv4))

if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: node_mgmt_ipv4_start
    Arg3: log level
    """
    log = Logger(__file__)

    ARGV_MAX = 4
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    log.clear()

    inv_file = sys.argv[1]
    node_mgmt_ipv4_start = sys.argv[2]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[3]
    else:
        log_level = None

    ipmi_data = InventoryModifyIPv4(
        log_level, inv_file, node_mgmt_ipv4_start)
