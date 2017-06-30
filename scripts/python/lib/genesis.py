# copyright 2017 IBM Corp.
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

import os.path
import yaml
import subprocess
import sys
import re

genesis_dir = 'cluster-genesis'
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
gen_path = FILE_PATH[:16 + FILE_PATH.find(genesis_dir)]
gen_scripts_path = gen_path + 'scripts'
gen_play_path = gen_path + 'playbooks'
gen_passive_path = gen_path + 'passive'


def load_localhost(filename):
    try:
        return yaml.safe_load(open(filename))
    except:
        print('Could not load file: ' + filename)
        sys.exit(1)


def container_running():
    cont_running = False
    lxc_ls_output = subprocess.check_output(['bash', '-c', 'sudo lxc-ls -f'])
    cont_running = re.search('^%s' % container_name, lxc_ls_output, re.MULTILINE)
    if cont_running:
        cont_running = True
    return cont_running


def container_addr():
    cont_address = None
    lxc_ls_output = subprocess.check_output(['bash', '-c', 'sudo lxc-ls -f'])
    cont_address = re.search('(\S+),\s+(\S+),', lxc_ls_output, re.MULTILINE).group(2)
    return cont_address


localhost_content = load_localhost(gen_path + "playbooks/host_vars/localhost")
container_name = localhost_content['container_name']
