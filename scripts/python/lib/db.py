#!/usr/bin/env python
"""Database"""

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

import os
import logging
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader

from lib.validate_config_schema import ValidateConfigSchema
from lib.validate_config_logic import ValidateConfigLogic
from lib.logger import Logger
from lib.genesis import GEN_PATH
from lib.exception import UserException


class Database(object):
    """Database

    Args:
        log (object): Log
        db_file (string): Database file
    """

    CFG_FILE = GEN_PATH + 'config.yml'
    INV_FILE = GEN_PATH + 'inventory.yml'
    FILE_MODE = 0o666

    def __init__(self):
        self.log = logging.getLogger(Logger.LOG_NAME)
        self.cfg_file = os.path.realpath(self.CFG_FILE)
        self.inv_file = os.path.realpath(self.INV_FILE)
        self.cfg = None
        self.inv = None

        # Check if config file exists
        if not os.path.isfile(self.cfg_file):
            msg = 'Could not find config file: ' + self.cfg_file
            self.log.error(msg)
            raise UserException(msg)

        # Create inventory file if it does not exist
        if not os.path.isfile(self.inv_file):
            os.mknod(self.inv_file, self.FILE_MODE)

    def _load_yaml_file(self, yaml_file):
        """Load from YAML file

        Exception:
            If load from file fails
        """

        try:
            return yaml.load(open(yaml_file), Loader=AttrDictYAMLLoader)
        except:
            msg = 'Could not load file: ' + yaml_file
            self.log.error(msg)
            raise UserException(msg)

    def _dump_yaml_file(self, yaml_file, content):
        """Dump to YAML file

        Exception:
            If dump to file fails
        """

        try:
            yaml.safe_dump(
                content,
                open(yaml_file, 'w'),
                indent=4,
                default_flow_style=False)
        except:
            msg = 'Could not dump inventory to file: ' + yaml_file
            self.log.error(msg)
            raise UserException

    def load_config(self):
        """Load config from database

        Returns:
            object: Config
        """

        self.cfg = self._load_yaml_file(self.cfg_file)
        return self.cfg

    def load_inventory(self):
        """Load inventory from database

        Returns:
            object: Inventory
        """

        self.inv = self._load_yaml_file(self.inv_file)
        return self.inv

    def dump_inventory(self, inv):
        """Dump inventory to database"""

        self.inv = inv
        self._dump_yaml_file(self.inv_file, inv)

    def validate_config(self, config_file):
        """Validate config"""

        if config_file is None:
            cfg_file = self.cfg_file
        else:
            cfg_file = os.path.realpath(config_file)
        self.cfg = self._load_yaml_file(cfg_file)
        self.log.setLevel(logging.INFO)
        schema = ValidateConfigSchema(self.cfg)
        schema.validate_config_schema()
        logic = ValidateConfigLogic(self.cfg)
        logic.validate_config_logic()