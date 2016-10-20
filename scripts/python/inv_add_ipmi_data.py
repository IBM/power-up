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
from pyghmi.ipmi import command as ipmi_command

from lib.inventory import Inventory
from lib.logger import Logger


class IpmiData(object):
    def __init__(self, log_level, inv_file, cfg_file):
        self.log = Logger(__file__)
        if log_level is not None:
            self.log.set_level(log_level)

        SNMP_PORT = 161

        IPMI_SYSTEM = b'System'
        IPMI_NODE1 = b'NODE 1'
        self.IPMI_CHASSIS_PART_NUMBER = b'Chassis part number'
        self.IPMI_CHASSIS_SERIAL_NUMBER = b'Chassis serial number'
        self.IPMI_MODEL = b'Model'
        self.IPMI_SERIAL_NUMBER = b'Serial Number'
        self.IPMI_SYSTEM_FIRMWARE = b'System Firmware'
        self.IPMI_PRODUCT_NAME = b'Product name'
        self.IPMI_OPENPOWER_FW = b'OpenPOWER Firmware'
        self.PPC64 = b'ppc64'

        self.inv_obj = Inventory(log_level, inv_file, cfg_file)

        for inv, key, _key, index, self.node in self.inv_obj.yield_nodes():
            ipmi_cmd = ipmi_command.Command(
                bmc=self.node[self.inv_obj.INV_IPV4_IPMI],
                userid=self.node[self.inv_obj.INV_USERID_IPMI],
                password=self.node[self.inv_obj.INV_PASSWORD_IPMI])
            fw = ipmi_cmd.get_inventory_of_component(
                self.IPMI_SYSTEM_FIRMWARE)
            try:
                if self.IPMI_PRODUCT_NAME in fw.keys():
                    if (fw[self.IPMI_PRODUCT_NAME] ==
                            self.IPMI_OPENPOWER_FW):
                        value = self.get_ipmi(
                            self.IPMI_SYSTEM_FIRMWARE,
                            self.IPMI_PRODUCT_NAME,
                            fw,
                            self.PPC64)
                        if value is not None:
                            self.inv_obj.add_to_node(
                                _key,
                                index,
                                self.inv_obj.INV_ARCHITECTURE,
                                value)
            except AttributeError:
                pass
            for ipmi_key, ipmi_value in ipmi_cmd.get_inventory():
                self.log.debug('%s: %s' % (ipmi_key, ipmi_value))
                if ipmi_key == IPMI_SYSTEM or ipmi_key == IPMI_NODE1:
                    value = self.get_ipmi(
                        ipmi_key,
                        self.IPMI_CHASSIS_PART_NUMBER,
                        ipmi_value)
                    if value is not None:
                        self.inv_obj.add_to_node(
                            _key,
                            index,
                            self.inv_obj.INV_CHASSIS_PART_NUMBER,
                            value)
                    value = self.get_ipmi(
                        ipmi_key,
                        self.IPMI_CHASSIS_SERIAL_NUMBER,
                        ipmi_value)
                    if value is not None:
                        self.inv_obj.add_to_node(
                            _key,
                            index,
                            self.inv_obj.INV_CHASSIS_SERIAL_NUMBER,
                            value)
                    value = self.get_ipmi(
                        ipmi_key,
                        self.IPMI_MODEL,
                        ipmi_value)
                    if value is not None:
                        self.inv_obj.add_to_node(
                            _key,
                            index,
                            self.inv_obj.INV_MODEL,
                            value)
                    value = self.get_ipmi(
                        ipmi_key,
                        self.IPMI_SERIAL_NUMBER,
                        ipmi_value)
                    if value is not None:
                        self.inv_obj.add_to_node(
                            _key,
                            index,
                            self.inv_obj.INV_SERIAL_NUMBER,
                            value)
                    if ipmi_key == IPMI_NODE1:
                        break

        self.inv_obj.dump()

    def get_ipmi(
        self,
            ipmi_key, ipmi_field, ipmi_value, inv_value=None):
        if ipmi_field in ipmi_value:
            self.log.info(
                self.node[self.inv_obj.INV_IPV4_IPMI] +
                ": '" +
                ipmi_key + '[' + ipmi_field + ']' +
                "' = " +
                ipmi_value[ipmi_field])
            if inv_value:
                return inv_value
            else:
                return str(ipmi_value[ipmi_field])
        else:
            self.log.info(
                self.node[self.inv_obj.INV_IPV4_IPMI] +
                ": '" +
                ipmi_key + '[' + ipmi_field + ']' +
                "' not found")
            return None

if __name__ == '__main__':
    log = Logger(__file__)

    ARGV_MAX = 4
    argv_count = len(sys.argv)
    if argv_count > ARGV_MAX:
        try:
            raise Exception()
        except:
            log.error('Invalid argument count')
            exit(1)

    cfg_file = sys.argv[1]
    inv_file = sys.argv[2]
    if argv_count == ARGV_MAX:
        log_level = sys.argv[3]
    else:
        log_level = None

    ipmi_data = IpmiData(log_level, inv_file, cfg_file)
