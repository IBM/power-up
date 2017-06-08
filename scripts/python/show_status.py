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
# python ./show_status.py /home/rhel72/config-test.yml DEBUG

from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals

import os
import sys
import subprocess

from lib import inventory
from lib.logger import Logger
from lib.ssh import SSH_CONNECTION
from lib import genesis

GEN_PATH = genesis.gen_path
GEN_CONTAINER_NAME = genesis.container_name
GEN_CONTAINER_RUNNING = genesis.container_running
GEN_CONTAINER_ADDR = genesis.container_addr
HOME_DIR = os.path.expanduser('~')

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


def main(log, inv_file):
    inv = inventory.Inventory(log, inv_file)

    print('\nBridge Status: \n')

    vlan_mgmt = inv.get_vlan_mgmt_network()
    bridge_vlan_mgmt = 'br' + str(vlan_mgmt)

    vlan_mgmt_client = inv.get_vlan_mgmt_client_network()
    bridge_vlan_mgmt_client = 'br' + str(vlan_mgmt_client)

    output = subprocess.check_output(['bash', '-c', 'brctl show'])
    if bridge_vlan_mgmt not in output:
        print('    Management VLAN not found')
    else:
        print(subprocess.check_output(
            ['bash', '-c', 'brctl show ' + bridge_vlan_mgmt]))
    if bridge_vlan_mgmt_client not in output:
        print('    Client VLAN not found')
    else:
        print(subprocess.check_output(
            ['bash', '-c', 'brctl show ' + bridge_vlan_mgmt_client]))

    print('Container Status: \n')
    output = subprocess.check_output(['bash', '-c', 'sudo lxc-ls -f'])
    if GEN_CONTAINER_NAME + ' ' in output:
        print(output)
    else:
        print('    ' + GEN_CONTAINER_NAME + ' container does not exist\n')

    if GEN_CONTAINER_RUNNING:
        if os.path.isfile(HOME_DIR + '/.ssh/id_rsa_ansible-generated'):
            key_filename = HOME_DIR + '/.ssh/id_rsa_ansible-generated'
            ssh_log_filename = FILE_PATH + '/gen_ssh.log'
            ssh_cont = SSH_CONNECTION(
                GEN_CONTAINER_ADDR,
                log=log,
                ssh_log=ssh_log_filename,
                username='deployer',
                look_for_keys=False,
                key_filename=key_filename)

            _, cobbler_running, _ = ssh_cont.send_cmd(
                'ps aux|grep cobbler')
            if 'root' in cobbler_running:
                print('cobbler is running')
                _, cobbler_status, _ = ssh_cont.send_cmd(
                    'sudo cobbler status')
                print(cobbler_status)
            else:
                print('cobbler is not running')

            _, dnsmasq_running, _ = ssh_cont.send_cmd(
                'ps aux|grep dnsmasq')
            if 'root' in dnsmasq_running:
                print('dnsmasq is running')
                _, dnsmasq_status, _ = ssh_cont.send_cmd(
                    'cat /var/lib/misc/dnsmasq.leases')
                print(dnsmasq_status)
            else:
                print('dnsmasq is not running')
            ssh_cont.close()
        else:
            print('\nContainer ssh key not available\n')
            log.info('Container ssh key not available')


def print_lines(str, line_list):
    """Splits str at newline (\n) characters, then prints the lines which
    contain elements from line_list. If line_list=[*] then all lines are
    printed."""
    str = str.splitlines()
    index = 0
    for _ in range(len(str)):
        for substr in line_list:
            if substr in str[index] or substr == '*':
                print(str[index])
        index += 1


def get_int_input(prompt_str, minn, maxx):
    while 1:
        try:
            input = int(raw_input(prompt_str))
            if not (minn <= input <= maxx):
                raise ValueError()
            else:
                break
        except ValueError:
            print("enter an integer between " +
                  str(minn) + ' and ' + str(maxx))
    return input


if __name__ == '__main__':
    """Show status of the Cluster Genesis environment

    Args:
        INV_FILE (string): Inventory file.
        LOG_LEVEL (string): Log level.

    Raises:
       Exception: If parameter count is invalid.
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
