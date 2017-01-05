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
import re
from orderedattrdict import AttrDict
from pysnmp.hlapi import *

from lib.utilities import *
from lib.logger import Logger

SNMP_PORT = 161
PUBLIC = 'public'
BRIDGE_MIB = 'BRIDGE-MIB'
DOT_1D_TP_FDB_PORT = 'dot1dTpFdbPort'


class GetMgmtSwitchConfig(object):
    def __init__(self, log_level):
        self.log = Logger(__file__)
        if log_level is not None:
            self.log.set_level(log_level)

    def get_port_mac(self, rack, switch_mgmt_ipv4):
        self.mac_port = []
        for (
            errorIndication,
            errorStatus,
            errorIndex,
            varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData(PUBLIC),
                UdpTransportTarget((switch_mgmt_ipv4, SNMP_PORT)),
                ContextData(),
                ObjectType(ObjectIdentity(BRIDGE_MIB, DOT_1D_TP_FDB_PORT)),
                lexicographicMode=False):

            if errorIndication:
                self.log.error(errorIndication)
                sys.exit(1)
            elif errorStatus:
                self.log.error('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                sys.exit(1)
            else:
                _dict = AttrDict()
                for varBind in varBinds:
                    m = re.search(
                        ('^%s::%s\.(' +
                         '(%s)' +
                         ' = ' +
                         '(\d+)$') % (
                             BRIDGE_MIB, DOT_1D_TP_FDB_PORT, PATTERN_MAC),
                        str(varBind))
                    mac = m.group(1)
                    port = int(m.group(3))
                    _dict[port] = mac
                    self.log.info(
                        'Rack: %s - MAC: %s - port: %d' % (rack, mac, port))
                    self.mac_port.append(_dict)
        return self.mac_port
