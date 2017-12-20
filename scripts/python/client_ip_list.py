#!/usr/bin/env python
# Copyright 2018 IBM Corp.
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

from lib.inventory import Inventory

inv = Inventory()

for index, hostname in enumerate(inv.yield_nodes_hostname()):
    ipaddr = inv.get_nodes_pxe_ipaddr(0, index)
    if index > 0:
        ipaddr = ',' + ipaddr
    print("%s" % ipaddr, end='')
print()
