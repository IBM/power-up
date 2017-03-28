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
import time
import re

from lib.inventory import Inventory
from lib.logger import Logger

PATTERN_IP = '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
PATTERN_MAC = '([0-9A-F]{2}[:-]){5}([0-9A-F]{2})'


class WatchLog(object):
    def __init__(self, log_file, inv_file, log):
        self.log_file = log_file
        self.inv = Inventory(log, inv_file)
        self.log = log

        self.system_count = self.inv.get_node_count()
        self.system_list = []

        try:
            f = open(self.log_file, 'r')
        except IOError:
            log.error('Cannot open file: %s' % self.log_file)
        else:
            f.close()

    def get_list(self, pattern, count):
        return_list = []

        with open(self.log_file, 'r') as f:
            for item in self.yield_tail_matches(f, pattern):
                return_list.append(item)
                log.info('Found Introspection Host IP: %s' % item)
                if len(return_list) >= count:
                    break

        return(return_list)

    def yield_tail_matches(self, log_file, pattern):
        pxelinux_sent_ips = []
        dhcp_releases = []

        log_file.seek(0, 2)
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(1)
                continue
            elif pattern in line:
                pxelinux_sent_ips.append(get_ip(line))
            elif 'DHCPRELEASE' in line:
                if get_ip(line) in pxelinux_sent_ips:
                    dhcp_releases.append(get_mac(line))
            elif 'DHCPACK' in line:
                if get_mac(line) in dhcp_releases:
                    yield get_ip(line)


def get_ip(string):
    return re.search(PATTERN_IP, string).group()


def get_mac(string):
    return re.search(PATTERN_MAC, string, re.I).group()


if __name__ == '__main__':
    """
    Arg1: log file to watch
    Arg2: pattern to extract
    Arg3: inventory file
    Arg4: log level
    """
    log = Logger(__file__)

    argv_count = len(sys.argv)
    if argv_count != 5:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            sys.exit(1)

    log_file = sys.argv[1]
    pattern = sys.argv[2]
    inv_file = sys.argv[3]
    log.set_level(sys.argv[4])

    l = WatchLog(log_file, inv_file, log)
    system_list = l.get_list(pattern, l.system_count)
    for ip in system_list:
        print(ip)
