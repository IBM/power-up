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

from lib.inventory import Inventory
from lib.ipmi_power import IpmiPower
from lib.logger import Logger


class IpmiPowerOff(object):
    def __init__(self, log, inv_file, time_out, wait):
        inv = Inventory(log, inv_file)
        self.ipmi_power = IpmiPower(log)
        self.log = log

        bmcs = []
        for rack_id, ipv4, userid, password in inv.yield_ipmi_access_info():
            bmc = {}
            bmc['rack_id'] = rack_id
            bmc['ipv4'] = ipv4
            bmc['userid'] = userid
            bmc['password'] = password

            _rc, _ = self.ipmi_power.is_power_off(bmc)
            if _rc:
                self.log.info(
                    'Already powered off - Rack: %s - IP: %s' %
                    (rack_id, ipv4))
            else:
                bmcs.append(bmc)
                self.ipmi_power.set_power_off(bmc)

        start_time = time.time()
        attempt = 1
        while bmcs:
            if time.time() > start_time + time_out:
                break
            time.sleep(wait)
            bmcs[:] = [
                bmc
                for bmc in bmcs
                if self._is_not_power_off(bmc, attempt) is not None]
            attempt += 1

        for bmc in bmcs:
            self.log.error(
                'Power off unsuccessful - Rack: %s - IP: %s - State: %s' %
                (bmc['rack_id'], bmc['ipv4'], bmc['power_state']))
        for bmc in bmcs:
            sys.exit(1)

    def _is_not_power_off(self, bmc, attempt):
        _rc, power_state = self.ipmi_power.is_power_off(bmc)
        if _rc:
            self.log.info(
                'Power off successful - Rack: %s - IP: %s' %
                (bmc['rack_id'], bmc['ipv4']))
            return None
        bmc['power_state'] = power_state
        self.log.debug(
            'Power off pending - Rack: %s - IP: %s - State: %s - Attempt: %s' %
            (bmc['rack_id'], bmc['ipv4'], bmc['power_state'], attempt))
        return bmc


if __name__ == '__main__':
    """
    Arg1: inventory file
    Arg2: time out
    Arg3: wait time
    Arg4: log level
    """
    LOG = Logger(__file__)

    if len(sys.argv) != 5:
        try:
            raise Exception()
        except Exception:
            LOG.error('Invalid argument count')
            sys.exit(1)

    INV_FILE = sys.argv[1]
    TIME_OUT = int(sys.argv[2])
    WAIT = int(sys.argv[3])
    LOG.set_level(sys.argv[4])

    IpmiPowerOff(LOG, INV_FILE, TIME_OUT, WAIT)
