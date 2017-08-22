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

from lib.inventory import Inventory
from lib.logger import Logger
from lib.switch import SwitchFactory


def main(log, inv_file):

    inv = Inventory(log, inv_file)
    userid = inv.get_userid_data_switch()
    password = inv.get_password_data_switch()
    switch_name = inv.get_data_switch_name()
    index = 0
    for ipv4 in inv.yield_data_switch_ip():
        switch = SwitchFactory.factory(
            log,
            switch_name,
            ipv4,
            userid,
            password,
            mode='active')
        switch_ip_to_port_to_macs = switch.show_mac_address_table(format='std')
        log.debug('switch_ip_to_port_to_macs')
        log.debug(switch_ip_to_port_to_macs)
        success = inv.add_data_switch_port_macs(ipv4, switch_ip_to_port_to_macs, index)
        if not success:
            sys.exit('Failed adding mac address table to inventory')
        index += 1


if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: log level
    """
    LOG = Logger(__file__)

    if len(sys.argv) != 3:
        try:
            raise Exception()
        except:
            LOG.error('Invalid argument count')
            sys.exit(1)

    INV_FILE = sys.argv[1]
    LOG.set_level(sys.argv[2])

    main(LOG, INV_FILE)
