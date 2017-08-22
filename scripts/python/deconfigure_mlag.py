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

from lib.logger import Logger
from lib.switch import SwitchFactory
from lib import genesis
from lib import inventory

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
ssh_log = FILE_PATH + '/gen_ssh.log'
GEN_PATH = genesis.gen_path


def main(log):
    inv_file = GEN_PATH + 'config.yml'
    inv = inventory.Inventory(log, inv_file)
    switch_class = inv.get_data_switch_class()
    userid = inv.get_userid_data_switch()
    password = inv.get_password_data_switch()
    for addr in inv.yield_data_switch_ip():
        sw = SwitchFactory.factory(log, switch_class, addr, userid, password, mode='active')
        mlag_ifcs = sw.show_mlag_interfaces()
        if "Unrecognized command" in mlag_ifcs:
            print('\nMLAG not configured on switch: {}'.format(addr))
        else:
            sw.deconfigure_mlag()


if __name__ == '__main__':
    """Remove mlag configuration from data switch.
    """
    LOG = Logger(__file__)
    LOG.set_level('INFO')
    main(LOG)
