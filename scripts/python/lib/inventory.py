"""Inventory"""

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

import logging
from enum import Enum
from orderedattrdict import AttrDict, DefaultAttrDict

from lib.db import Database
from lib.logger import Logger


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


# Python 3
# class Inventory(metaclass=Singleton):
class Inventory(object):
    __metaclass__ = Singleton
    """Inventory

    Args:
        log (object): Log
        inv_file (string): Inventory file
    """

    class SwitchType(Enum):
        MGMT, DATA = range(2)

    class InvKey(object):
        NODES = 'nodes'
        LABEL = 'label'
        HOSTNAME = 'hostname'
        USERID = 'userid'
        PASSWORD = 'password'
        SSH_KEY = 'ssh_key'
        ROOM = 'room'
        ROW = 'row'
        CELL = 'cell'
        IPADDR = 'ipaddr'
        IPMI = 'ipmi'
        PXE = 'pxe'
        DATA = 'data'
        SWITCHES = 'switches'
        SWITCHES_IPMI = 'switches_ipmi'
        SWITCHES_PXE = 'switches_pxe'
        PORTS = 'ports'
        PORTS_IPMI = 'ports_ipmi'
        PORTS_PXE = 'ports_pxe'
        RACK_ID = 'rack_id'
        USERID = 'userid'
        PASSWORD = 'password'
        DEVICES = 'devices'
        DEVICES_PXE = 'devices_pxe'

    def __init__(self):
        self.log = logging.getLogger(Logger.LOG_NAME)
        self.dbase = Database()

        self.inv = AttrDict()
        inv = self.dbase.load_inventory()
        if inv is not None:
            self.inv = inv

        self.switch = None
        self.switch_type = None

        if self.InvKey.NODES not in self.inv:
            self.inv.nodes = []

        # Order is only kept in Python 3.6 and above
        # self.nodes = AttrDict({
        #     self.InvKey.LABEL: 'a',
        #     self.InvKey.HOSTNAME: 'b',
        #     self.InvKey.PORT: 'c'})

        self.nodes = AttrDict()
        self.nodes[self.InvKey.LABEL] = []
        self.nodes[self.InvKey.HOSTNAME] = []
        self.nodes[self.InvKey.RACK_ID] = []
        self.nodes[self.InvKey.IPMI] = AttrDict()
        self.nodes[self.InvKey.PXE] = AttrDict()

        self.nodes[self.InvKey.IPMI][self.InvKey.SWITCHES] = []
        self.nodes[self.InvKey.IPMI][self.InvKey.PORTS] = []
        self.nodes[self.InvKey.IPMI][self.InvKey.USERID] = []
        self.nodes[self.InvKey.IPMI][self.InvKey.PASSWORD] = []
        self.nodes[self.InvKey.PXE][self.InvKey.PORTS] = []
        self.nodes[self.InvKey.PXE][self.InvKey.DEVICES] = []
        self.nodes[self.InvKey.PXE][self.InvKey.SWITCHES] = []

    def add_nodes_hostname(self, hostname):
        self.nodes.hostname.append(hostname)

    def add_nodes_label(self, label):
        self.nodes.label.append(label)

    def add_nodes_rack_id(self, rack_id):
        self.nodes.rack_id.append(rack_id)

    def add_nodes_switches_ipmi(self, switches):
        self.nodes.ipmi.switches.append(switches)

    def add_nodes_switches_pxe(self, switches):
        self.nodes.pxe.switches.append(switches)

    def add_nodes_ports_ipmi(self, ports):
        self.nodes.ipmi.ports.append(ports)

    def add_nodes_ports_pxe(self, ports):
        self.nodes.pxe.ports.append(ports)

    def add_nodes_userid_ipmi(self, userid):
        self.nodes.ipmi.userid.append(userid)

    def add_nodes_password_ipmi(self, password):
        self.nodes.ipmi.password.append(password)

    def add_nodes_devices_pxe(self, dev):
        self.nodes.pxe.devices.append(dev)

    def _flatten(self, data):
        def items():
            for key, value in data.iteritems():
                if isinstance(value, dict):
                    for subkey, subvalue in self._flatten(value).iteritems():
                        yield key + '.' + subkey, subvalue
                else:
                    yield key, value
        return AttrDict(items())

    def update_nodes(self):
        nodes = []
        flat = self._flatten(self.nodes)

        for item_key, item_values in flat.iteritems():
            for index, item_value in enumerate(item_values):
                if len(nodes) <= index:
                    nodes.append(DefaultAttrDict(dict))
                if '.' in item_key:
                    keys = item_key.split('.')
                    nodes[index][keys[0]][keys[1]] = item_value
                else:
                    nodes[index][item_key] = item_value

        self.inv.nodes = nodes
        self.dbase.dump_inventory(self.inv)
