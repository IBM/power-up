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
import readline
from pyghmi.ipmi import command as ipmi_command
from pyghmi import exceptions as pyghmi_exception

from lib.inventory import Inventory
from lib.logger import Logger


def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()


def Power_Status(log, inv_file):
    inv = Inventory(log, inv_file)

    print('Systems in Cluster Genesis inventory: ')

    systems = []

    for rack, ipv4, user, passwd in inv.yield_ipmi_access_info():
        ipmi_cmd = ipmi_command.Command(
            bmc=ipv4,
            userid=user,
            password=passwd)
        try:
            status = ipmi_cmd.get_power()
            systems.append({'ipv4': ipv4, 'user': user, 'password': passwd})
        except pyghmi_exception.IpmiException as error:
            print(
                'BMC Power status failed - Rack: %s - IP: %s, %s' %
                (rack, ipv4, str(error)))

        print('Rack: {} - IP: {} Power status: {}'.format(rack, ipv4, status))

    resp = rlinput('Reset the BMCs for the above responding systems? (y/n)')
    if resp == 'n' or resp == 'N':
        sys.exit(0)

    for system in systems:
        print(system)
        print(system['ipv4'])
        ipmi_cmd = ipmi_command.Command(
            bmc=system['ipv4'],
            userid=system['user'],
            password=system['password'])

        ipmi_cmd.reset_bmc()


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
            sys.exit('Invalid argument count')

    INV_FILE = sys.argv[1]
    LOG.set_level(sys.argv[2])
    Power_Status(LOG, INV_FILE)
