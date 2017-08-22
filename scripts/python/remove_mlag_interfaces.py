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

import os
import readline
import re
import sys

from lib.logger import Logger
from lib.switch import SwitchFactory
from lib import genesis
from lib import inventory
from lib.switch_exception import SwitchException

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
ssh_log = FILE_PATH + '/gen_ssh.log'
GEN_PATH = genesis.gen_path


def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()


def main(log):
    inv_file = GEN_PATH + 'config.yml'
    inv = inventory.Inventory(log, inv_file)
    switch_class = inv.get_data_switch_class()
    userid = inv.get_userid_data_switch()
    password = inv.get_password_data_switch()
    for addr in inv.yield_data_switch_ip():
        sw = SwitchFactory.factory(log, switch_class, addr, userid, password, mode='active')
        try:
            mlag_ifcs = sw.show_mlag_interfaces()
        except SwitchException as exc:
            print(exc)
            print('Unable to retrieve any mlag interfaces')
            sys.exit(1)
        mlag_ifcs = sw.show_mlag_interfaces()
        print('\n       MLAG interface summary for switch: {}'.format(addr))
        print(mlag_ifcs)
        mlag_ifcs = mlag_ifcs.splitlines()
        ifc_list = ''
        for line in mlag_ifcs:
            match = re.search(r'\d+\s+Mpo(\d+)', line)
            if match:
                ifc_list = ifc_list + match.group(1) + " "
                log.debug('Found MLAG interface: ' + match.group(1))
        if ifc_list == '':
            print('No MLAG interfaces found in switch {} '.format(addr))
            continue
        ifc_list = ifc_list[:-1]
        log.debug('MLAG interface list: ' + ifc_list)
        ifc_list = rlinput('Enter mlag port channels to remove :', ifc_list)
        ifc_list = ifc_list.split(' ')
        ifc_list = [int(d) for d in ifc_list]
        print('Removing interfaces: ')
        print(ifc_list)
        for ifc in ifc_list:
            sw.set_mtu_for_mlag_port_channel(ifc, 0)
            sw.remove_mlag_interface(ifc)
            sw.set_mtu_for_port(ifc, 0)


if __name__ == '__main__':
    """Remove mlag port channels from data switch so that mac addresses show up
    in the switch.
    """
    LOG = Logger(__file__)
    LOG.set_level('INFO')
    main(LOG)
