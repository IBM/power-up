"""Switch configuration."""

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

from lib import Lenovo
from lib import Mellanox


class SwitchFactory(object):
    """Common switch configuration."""
    def __init__(self, log, switch_type, ip_addr, userid, password):
        pass

    @staticmethod
    def factory(log, switch_type, ip_addr, userid, password):
        """Return management switch model object.

        Args:
            log (:obj:`Logger`): Log object.
            inv (:obj:`Inventory`): Inventory object.
            switch_type (enum): Switch type.

        Raises:
            Exception: If management switch class is invalid.
        """
        if switch_type == 'lenovo':
            return Lenovo.switch.factory(log, ip_addr, userid, password)
        if switch_type == 'mellanox':
            return Mellanox.switch.factory(log, ip_addr, userid, password)
        try:
            raise Exception()
        except:
            print('Invalid switch class')
            log.error('Invalid switch class')
            sys.exit(1)
