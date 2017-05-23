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

import sys
from lib import inventory
from lib.logger import Logger
import mellanox_switch


def main(log, inv_file):

    inv = inventory.Inventory(log, inv_file)
    switch = mellanox_switch.MellanoxSwitch(log)
    switch_ip_to_port_to_macs = switch.get_macs(inv)
    success = inv.add_data_switch_port_macs(switch_ip_to_port_to_macs)
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: log level
    """
    LOG = Logger(__file__)

    ARGV_MAX = 3
    ARGV_COUNT = len(sys.argv)
    if ARGV_COUNT > ARGV_MAX:
        try:
            raise Exception()
        except:
            LOG.error('Invalid argument count')
            sys.exit(1)

    INV_FILE = sys.argv[1]
    LOG.set_level(sys.argv[2])

    main(LOG, INV_FILE)
