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
from pyghmi.ipmi import command as ipmi_command
from pyghmi import exceptions as pyghmi_exception

from lib.inventory import Inventory
from lib.ipmi_power import IpmiPower
from lib.logger import Logger
from get_dhcp_lease_info import GetDhcpLeases


class IpmiPowerPXE(object):
    def __init__(self, log, inv_file, dhcp_leases_path, time_out, wait):
        self.log = log

        inv = Inventory(self.log, inv_file)
        self.ipmi_power = IpmiPower(self.log)

        # Get list of BMCs from DHCP lease file
        dhcp_leases = GetDhcpLeases(dhcp_leases_path, self.log)
        bmc_leases = dhcp_leases.get_mac_ip()
        bmc_list = []
        for mac, ipv4 in bmc_leases.items():
            bmc = {}
            bmc['ipv4'] = ipv4
            bmc['rack_id'] = 'unknown'
            for userid, password in inv.yield_ipmi_credential_sets():
                bmc['userid'] = userid
                bmc['password'] = password

                self.log.debug(
                    'Trying IP: %s  userid: %s  password: %s' %
                    (ipv4, userid, password))

                try:
                    _rc, _ = self.ipmi_power.is_power_off(bmc)
                except SystemExit:
                    continue

                bmc_list.append(bmc)
                break

        # Power off
        for bmc in bmc_list:
            _rc, _ = self.ipmi_power.is_power_off(bmc)
            if _rc:
                self.log.debug(
                    'Already powered off - Rack: %s - IP: %s' %
                    (bmc['rack_id'], bmc['ipv4']))
            else:
                self.ipmi_power.set_power_off(bmc)
        start_time = time.time()
        attempt = 1
        bmcs = list(bmc_list)
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

        # Set boot device to pxe (not persistent)
        bootdev = 'pxe'
        persist = False
        for bmc in bmc_list:
            ipmi_cmd = ipmi_command.Command(
                bmc=bmc['ipv4'],
                userid=bmc['userid'],
                password=bmc['password'])
            try:
                ipmi_cmd.set_bootdev(bootdev, persist)
            except pyghmi_exception.IpmiException as error:
                log.error(
                    'set_bootdev failed (device=%s persist=%s) - '
                    'IP: %s, %s' %
                    (bootdev, persist, bmc['ipv4'], str(error)))
                sys.exit(1)
            log.info(
                'set_bootdev success (device=%s persist=%s) - '
                'IP: %s' %
                (bootdev, persist, bmc['ipv4']))

        # Power on
        for bmc in bmc_list:
            _rc, _ = self.ipmi_power.is_power_on(bmc)
            if _rc:
                self.log.info(
                    'Already powered on - Rack: %s - IP: %s' %
                    (bmc['rack_id'], bmc['ipv4']))
            else:
                self.ipmi_power.set_power_on(bmc)
        start_time = time.time()
        attempt = 1
        bmcs = list(bmc_list)
        while bmcs:
            if time.time() > start_time + time_out:
                break
            time.sleep(wait)
            bmcs[:] = [
                bmc
                for bmc in bmcs
                if self._is_not_power_on(bmc, attempt) is not None]
            attempt += 1

        for bmc in bmcs:
            self.log.error(
                'Power on unsuccessful - Rack: %s - IP: %s - State: %s' %
                (bmc['rack_id'], bmc['ipv4'], bmc['power_state']))
        for bmc in bmcs:
            sys.exit(1)

    def _is_not_power_on(self, bmc, attempt):
        _rc, power_state = self.ipmi_power.is_power_on(bmc)
        if _rc:
            self.log.info(
                'Power on successful - Rack: %s - IP: %s' %
                (bmc['rack_id'], bmc['ipv4']))
            return None
        bmc['power_state'] = power_state
        self.log.debug(
            'Power on pending - Rack: %s - IP: %s - State: %s - Attempt: %s' %
            (bmc['rack_id'], bmc['ipv4'], bmc['power_state'], attempt))
        return bmc

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
    Arg2: dhcp leases file path
    Arg3: time out
    Arg4: wait time
    Arg5: log level
    """
    LOG = Logger(__file__)

    if len(sys.argv) != 6:
        try:
            raise Exception()
        except Exception:
            LOG.error('Invalid argument count')
            sys.exit(1)

    INV_FILE = sys.argv[1]
    DHCP_LEASES_PATH = sys.argv[2]
    TIME_OUT = int(sys.argv[3])
    WAIT = int(sys.argv[4])
    LOG.set_level(sys.argv[5])

    IpmiPowerPXE(LOG, INV_FILE, DHCP_LEASES_PATH, TIME_OUT, WAIT)
