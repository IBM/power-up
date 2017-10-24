#!/usr/bin/env python
"""Cluster Genesis 'teardown' command"""

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
import subprocess
import os

import lib.argparse_teardown as argparse_teardown
from lib.logger import Logger
from lib.config import Config
# from lib.container import Container
from lib.genesis import GEN_SCRIPTS_PATH


class Teardown(object):
    """Cluster Genesis 'teardown' command

    Args:
        log(object): log
    """

    def __init__(self, args, log=None):
        if log is not None:
            cfg = Config()
            log.set_level(cfg.get_globals_log_level())
        self.args = args
        self.log = log

    def _destroy_deployer_container(self):
        print('teardown.py - destroy deployer container')
        sys.exit('Teardown container not implemented')

    def _teardown_deployer_networks(self):
        self.log.info('Teardown deployer networks')
        os.chdir(GEN_SCRIPTS_PATH + '/python')
        subprocess.check_output(['bash', '-c',
                                 "sudo setcap 'cap_net_raw,cap_net_admin+eip'"
                                 " $(readlink -f $(which python))"])
        p = subprocess.Popen(GEN_SCRIPTS_PATH +
                             "/python/teardown_deployer_networks.py")
        out, err = p.communicate()
        subprocess.check_output(['bash', '-c',
                                 "sudo setcap 'cap_net_raw,cap_net_admin-eip'"
                                 " $(readlink -f $(which python))"])

    def _teardown_deployer_gateway(self):
        print('teardown.py - teardown deployer gateway')
        sys.exit('Teardown deployer gateway not implemented')

    def launch(self):
        """Launch actions"""

        # Determine which subcommand was specified
        if self.args.deployer:
            if self.args.networks:
                self._teardown_deployer_networks()
            if self.args.container:
                self._destroy_deployer_container()
            if self.args.gateway:
                self._teardown_deployer_gateway()
            return


if __name__ == '__main__':
    try:
        a = argparse_teardown.get_parsed_args()
    except SystemExit:
        sys.exit('Invalid teardown option')
    TEARDOWN = Teardown(argparse_teardown.get_parsed_args(),
                        Logger(Logger.LOG_NAME))
    TEARDOWN.launch()
