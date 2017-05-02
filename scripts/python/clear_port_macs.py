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
    switch.clear_mac_address_table(inv)


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
            exit(1)

    inv_file = sys.argv[1]
    if argv_count == ARGV_MAX:
        log.set_level(sys.argv[2])

    main(log, inv_file)
