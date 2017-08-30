#!/usr/bin/env python
"""Create inventory"""

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

from lib.logger import Logger
from lib.config import Config
from lib.inv_nodes import InventoryNodes


class InventoryCreate(object):
    """Create inventory

    Args:
        log(object): log
    """

    def __init__(self, log=None):
        if log is not None:
            cfg = Config()
            log.set_level(cfg.get_globals_log_level())

    def create(self):
        """Create inventory"""

        nodes = InventoryNodes()
        nodes.create_nodes()


if __name__ == '__main__':
    INV = InventoryCreate(Logger(Logger.LOG_NAME))
    INV.create()
