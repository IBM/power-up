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

import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader

from lib.validate_config_schema import ValidateConfigSchema
from lib.validate_config_logic import ValidateConfigLogic


class Database(object):
    """Database

    Args:
        log (object): Log
        db_file (string): Database file
    """

    def __init__(self, log, db_file):
        self.log = log
        self.file = os.path.abspath(
            os.path.dirname(os.path.abspath(db_file)) +
            os.path.sep +
            os.path.basename(db_file))
        self.inv = None

        if not os.path.isfile(self.file):
            try:
                raise Exception()
            except Exception:
                self.log.error('Could not find: ' + self.file)
                sys.exit(1)

    def _load_yaml_file(self):
        """Load inventory from YAML file

        Exception:
            If load from file fails
        """

        try:
            self.inv = yaml.load(open(self.file), Loader=AttrDictYAMLLoader)
        except:
            self.log.error('Could not load file: ' + self.file)
            sys.exit(1)

    def _dump_yaml_file(self):
        """Dump inventory to YAML file

        Exception:
            If dump to file fails
        """

        try:
            yaml.safe_dump(
                self.inv,
                open(self.file, 'w'),
                indent=4,
                default_flow_style=False)
        except:
            self.log.error(
                'Could not dump inventory to file: ' + self.file)
            sys.exit(1)

    def load_inventory(self):
        """Load inventory from database

        Returns:
            object: Inventory
        """

        self._load_yaml_file()
        return self.inv

    def dump_inventory(self):
        """Dump inventory to database"""

        self._dump_yaml_file()

    def validate_config(self):
        """Validate config"""

        self._load_yaml_file()
        schema = ValidateConfigSchema(self.log, self.inv)
        schema.validate_config_schema()
        logic = ValidateConfigLogic(self.log, self.inv)
        logic.validate_config_logic()
