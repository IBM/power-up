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
from pyghmi.ipmi import command as ipmi_command
from pyghmi import exceptions as pyghmi_exception

from lib.inventory import Inventory
from lib.logger import Logger


class IpmiSetBootdev(object):
    def __init__(self, log_level, inv_file, bootdev, persist=False):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        if type(persist) is not bool:
            persist = (persist == 'True')

        inv = Inventory(log_level, inv_file)
        for rack_id, ipv4, _userid, _password in inv.yield_ipmi_access_info():
            ipmi_cmd = ipmi_command.Command(
                bmc=ipv4,
                userid=_userid,
                password=_password)

            try:
                rc = ipmi_cmd.set_bootdev(bootdev, persist)
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'set_bootdev failed (device=%s persist=%s) - '
                    'Rack: %s - IP: %s, %s' %
                    (bootdev, persist, rack_id, ipv4, str(error)))
                # sys.exit(1)

            if 'error' in rc:
                log.error(
                    'set_bootdev failed (device=%s persist=%s) - '
                    'Rack: %s - IP: %s, %s' %
                    (bootdev, persist, rack_id, ipv4, str(rc['error'])))
                # sys.exit(1)

            time.sleep(5)

            try:
                rc = ipmi_cmd.get_bootdev()
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'get_bootdev failed - '
                    'Rack: %s - IP: %s, %s' %
                    (rack_id, ipv4, str(error)))
                # sys.exit(1)

            if 'error' in rc:
                log.error(
                    'get_bootdev failed - '
                    'Rack: %s - IP: %s, %s' %
                    (rack_id, ipv4, str(rc['error'])))
                # sys.exit(1)
            elif (rc['bootdev'] == bootdev and
                    str(rc['persistent']) == str(persist)):
                log.info(
                    'set_bootdev successful (device=%s persist=%s) - '
                    'Rack: %s - IP: %s' %
                    (bootdev, persist, rack_id, ipv4))
            else:
                log.error(
                    'set_bootdev failed - set: (device=%s persist=%s) '
                    'but read: (device=%s persist=%s) - '
                    'Rack: %s - IP: %s' %
                    (bootdev, persist, rc['bootdev'], rc['persistent'],
                     rack_id, ipv4))
                # sys.exit(1)


if __name__ == '__main__':
    log = Logger(__file__)

    ARGV_MAX = 5
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    log.clear()

    inv_file = sys.argv[1]
    bootdev = sys.argv[2]
    persist = sys.argv[3]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[4]
    else:
        log_level = None
    ipmi_data = IpmiSetBootdev(log_level, inv_file, bootdev, persist)
