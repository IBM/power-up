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
import sys
import os.path
import yaml
from orderedattrdict.yamlutils import AttrDictYAMLLoader

ARGV_MAX = 3
ARGV_COUNT = len(sys.argv)
if ARGV_COUNT > ARGV_MAX:
    try:
        raise Exception()
    except:
        print('Invalid argument count')
        sys.exit(1)


def abs_path(file_):
    return os.path.abspath(
        os.path.dirname(os.path.abspath(file_)) +
        os.path.sep +
        os.path.basename(file_))


YAML_FILE = abs_path(sys.argv[1])

try:
    CONTENT = yaml.load(open(YAML_FILE), Loader=AttrDictYAMLLoader)
except:
    print('Could not load file: ' + YAML_FILE)
    sys.exit(1)

if len(sys.argv) == ARGV_MAX:
    YAML_FILE = abs_path(sys.argv[2])

try:
    yaml.dump(
        CONTENT,
        open(YAML_FILE, 'w'),
        indent=4,
        default_flow_style=False)
except:
    print('Could not dump file: ' + YAML_FILE)
    sys.exit(1)
