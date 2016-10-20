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
from pyghmi.ipmi import command as ipmi_command
from pyghmi import exceptions as pyghmi_exception
import time

from lib.inventory import Inventory
from lib.logger import Logger

WAIT = True
OFF = 'off'
POWERSTATE = 'powerstate'


class IpmiPowerOff(object):
    def __init__(self, log_level, inv_file):
        log = Logger(__file__)
        if log_level is not None:
            log.set_level(log_level)

        inv = Inventory(log_level, inv_file)
        for rack_id, ipv4, _userid, _password in inv.yield_ipmi_access_info():
            ipmi_cmd = ipmi_command.Command(
                bmc=ipv4,
                userid=_userid,
                password=_password)

            try:
                rc = ipmi_cmd.get_power()
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'Power status failed - Rack: %s - IP: %s, %s' %
                    (rack_id, ipv4, str(error)))
                # sys.exit(1)

            if rc.get(POWERSTATE) == OFF:
                log.info(
                    'Already powered off - Rack: %s - IP: %s' %
                    (rack_id, ipv4))
                continue

            try:
                rc = ipmi_cmd.set_power(OFF, WAIT)
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'Power off failed - Rack: %s - IP: %s, %s' %
                    (rack_id, ipv4, str(error)))
                # sys.exit(1)

            if rc.get(POWERSTATE) != OFF:
                log.error(
                    'Power off did not occur - Rack: %s - IP: %s' %
                    (rack_id, ipv4))
                # sys.exit(1)

            log.info('Power off - Rack: %s - IP: %s' % (rack_id, ipv4))

        time.sleep(180)

if __name__ == '__main__':
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
        log_level = sys.argv[2]
    else:
        log_level = None
    ipmi_data = IpmiPowerOff(log_level, inv_file)
