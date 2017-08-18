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

from lib import lenovo
from lib import mellanox
from lib import cisco


class SwitchFactory(object):
    """Common switch configuration."""
    def __init__(self, log, switch_type, host=None, userid=None, password=None, mode=None, outfile=None):
        pass

    @staticmethod
    def factory(log, switch_type, host=None, userid=None, password=None, mode='passive', outfile='switch_cmds.txt'):
        """Return management switch model object.

        Args:
            log (:obj:`Logger`): Log object.
            inv (:obj:`Inventory`): Inventory object.
            switch_type (enum): Switch type.

        Raises:
            Exception: If management switch class is invalid.
        """
        if switch_type in 'lenovo Lenovo LENOVO':
            return lenovo.switch.factory(log, host, userid, password, mode, outfile)
        if switch_type in 'mellanox Mellanox MELLANOX':
            return mellanox.switch.factory(log, host, userid, password, mode, outfile)
        if switch_type in 'cisco Cisco CISCO':
            return cisco.switch.factory(log, host, userid, password, mode, outfile)
        try:
            raise Exception()
        except:
            print('Invalid switch class')
            log.error('Invalid switch class')
            sys.exit(1)
