#!/usr/bin/env python
"""Validate config"""

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

from lib.logger import Logger
from lib.db import Database


class ValidateConfig(object):
    """Validate config

    Args:
        log (object): Log
        cfg_file (string): COnfig file
    """

    def __init__(self, log, cfg_file):
        self.log = log
        self.cfg_file = cfg_file

    def validate_config(self):
        """Validate config"""

        dbase = Database(self.log, self.cfg_file)
        dbase.validate_config()


if __name__ == '__main__':
    """
    Arg1: config file
    Arg2: log level
    """
    LOG = Logger(__file__)

    if len(sys.argv) != 3:
        try:
            raise Exception()
        except Exception:
            LOG.error('Invalid argument count')
            sys.exit(1)

    CFG_FILE = sys.argv[1]
    LOG.set_level(sys.argv[2])

    VAL_CFG = ValidateConfig(LOG, CFG_FILE)
    VAL_CFG.validate_config()
