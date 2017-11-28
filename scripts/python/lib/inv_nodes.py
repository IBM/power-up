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

import lib.logger as logger
from lib.config import Config
from lib.inventory import Inventory


class InventoryNodes(object):
    SWITCH_NOT_FOUND = \
        "Node template '%s' did not have corresponding management switch '%s'"

    def __init__(self):
        self.log = logger.getlogger()
        self.inv = Inventory()

    def __del__(self):
        self.inv.update_nodes()

    def create_nodes(self):
        cfg = Config()
        # Iterate over node templates
        for index_ntmplt in cfg.yield_ntmpl_ind():
            # Get Label
            label = cfg.get_ntmpl_label(index_ntmplt)
            # Get Hostname
            hostname = cfg.get_ntmpl_os_hostname_prefix(index_ntmplt)
            if hostname is None:
                hostname = label
            # Get Rack
            switch_label = cfg.get_ntmpl_phyintf_ipmi_switch(index_ntmplt, 0)
            switch_index = cfg.get_sw_mgmt_index_by_label(switch_label)
            if switch_index is None:
                node_template = cfg.get_ntmpl_label(index_ntmplt)
                self.log.error(self.SWITCH_NOT_FOUND % (
                    node_template, switch_label))
            # Iterate over client systems
            index_host = 0
            for index_port in cfg.yield_ntmpl_phyintf_ipmi_pt_ind(
                    index_ntmplt, 0):
                # Set Label
                self.inv.add_nodes_label(label)
                # Set Hostname
                self.inv.add_nodes_hostname(
                    hostname + '-' + str(index_host + 1))
                # Set Rack ID
                switch_label = cfg.get_ntmpl_phyintf_ipmi_switch(
                    index_ntmplt, 0)
                switch_index = cfg.get_sw_mgmt_index_by_label(switch_label)
                self.inv.add_nodes_rack_id(cfg.get_sw_mgmt_rack_id(
                    switch_index))

                ports_ipmi = []
                ports_pxe = []
                switches_ipmi = []
                switches_pxe = []
                devices_pxe = []
                # Iterate over IPMI members
                for index_ipmi in cfg.yield_ntmpl_phyintf_ipmi_ind(
                        index_ntmplt):
                    # Create client system IPMI switch list
                    switches_ipmi.append(cfg.get_ntmpl_phyintf_ipmi_switch(
                        index_ntmplt, index_ipmi))
                    # Create client system PXE switch list
                    switches_pxe.append(cfg.get_ntmpl_phyintf_pxe_switch(
                        index_ntmplt, index_ipmi))
                    # Create client system IPMI port list
                    ports_ipmi.append(cfg.get_ntmpl_phyintf_ipmi_ports(
                        index_ntmplt, index_ipmi, index_port))
                    # Create client system PXE port list
                    ports_pxe.append(cfg.get_ntmpl_phyintf_pxe_ports(
                        index_ntmplt, index_ipmi, index_port))
                    # Create client PXE network device list
                    devices_pxe.append(cfg.get_ntmpl_phyintf_pxe_dev(
                        index_ntmplt, index_ipmi))
                # Set client system IPMI switches
                self.inv.add_nodes_switches_ipmi(switches_ipmi)
                # Set client system PXE switches
                self.inv.add_nodes_switches_pxe(switches_pxe)
                # Set client system IPMI ports
                self.inv.add_nodes_ports_ipmi(ports_ipmi)
                # Set client system PXE ports
                self.inv.add_nodes_ports_pxe(ports_pxe)
                # Set client system IPMI userids
                self.inv.add_nodes_userid_ipmi(cfg.get_ntmpl_ipmi_userid(
                    index_ntmplt))
                # Set client system IPMI passwords
                self.inv.add_nodes_password_ipmi(cfg.get_ntmpl_ipmi_password(
                    index_ntmplt))
                # Set PXE network device
                self.inv.add_nodes_devices_pxe(cfg.get_ntmpl_phyintf_pxe_dev(
                    index_ntmplt))
                index_host += 1
        self.log.info('Successfully created inventory file')
