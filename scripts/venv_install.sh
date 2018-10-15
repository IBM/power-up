#!/bin/bash
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

python3.6 -m venv ${1}pup-venv
source ${1}pup-venv/bin/activate
pip install --upgrade pip
pip install --upgrade setuptools==40.0.0
pip install \
    'ansible==2.7.0' \
    'ansible-vault==1.2.0' \
    'click==7.0' \
    'filelock==3.0.9' \
    'gitpython==2.1.11' \
    'jsl==0.2.4' \
    'jsonschema==2.6.0' \
    'netaddr==0.7.19' \
    'orderedattrdict==1.5' \
    'paramiko==2.4.2' \
    'pip2pi==0.7.0' \
    'pyaml==17.12.1' \
    'pyasn1==0.4.4' \
    'pycrypto==2.6.1' \
    'pyghmi==1.2.14' \
    'pyroute2==0.5.3' \
    'pysnmp==4.4.6' \
    'tabulate==0.8.2' \
    'wget==3.2'
deactivate
