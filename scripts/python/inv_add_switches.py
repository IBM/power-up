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

from lib.inventory import Inventory
from lib.logger import Logger


class InventoryAddSwitches(object):
    def __init__(self, log_level, inv_file):
        log = Logger(__file__)

        inv = Inventory(log_level, inv_file)
        inv.add_switches()

if __name__ == '__main__':
    """
    Arg1: config file
    Arg2: inventory file
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

    inv_file = sys.argv[1]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[2]
    else:
        log_level = None

    ipmi_data = InventoryAddSwitches(log_level, inv_file)
