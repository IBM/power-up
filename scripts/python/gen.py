#!/usr/bin/env python
"""Cluster Genesis 'gen' command"""

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
import os
import subprocess
import getpass

import configure_mgmt_switches
import lxc_conf
import lib.argparse_gen as argparse_gen
from lib.logger import Logger
from lib.config import Config
from lib.db import Database
from lib.container import Container
from lib.exception import UserException
from lib.genesis import GEN_SCRIPTS_PATH


class Gen(object):
    """Cluster Genesis 'gen' command

    Args:
        log(object): log
    """

    ROOTUSER = 'root'

    def __init__(self, args, log=None):
        if log is not None:
            try:
                cfg = Config()
            except UserException as exc:
                print(exc)
                sys.exit(1)
            try:
                log.set_level(cfg.get_globals_log_level())
            except:
                print('Unable to read log level from config file')
        self.args = args

    def _check_root_user(self, cmd):
        if getpass.getuser() != self.ROOTUSER:
            print(
                "Error: '%s %s ...' should be run as root" %
                (sys.argv[0], cmd),
                file=sys.stderr)
            sys.exit(1)

    def _check_non_root_user(self, cmd):
        if getpass.getuser() == self.ROOTUSER:
            print(
                "Error: '%s %s ...' should not be run as root" %
                (sys.argv[0], cmd),
                file=sys.stderr)
            sys.exit(1)

    def _config_mgmt_switches(self):
        try:
            configure_mgmt_switches.configure_mgmt_switches()
        except UserException as exc:
            print('Error occured while configuring managment switches: \n' +
                  exc)
            sys.exit(1)

    def _create_bridges(self):
        # enable_deployer_networks.enable_deployer_network()
        os.chdir(GEN_SCRIPTS_PATH + '/python')
        subprocess.check_output(['bash', '-c',
                                 "sudo setcap 'cap_net_raw,cap_net_admin+eip'"
                                 " $(readlink -f $(which python))"])
        p = subprocess.Popen(GEN_SCRIPTS_PATH +
                             "/python/enable_deployer_networks.py")
        out, err = p.communicate()
        subprocess.check_output(['bash', '-c',
                                 "sudo setcap 'cap_net_raw,cap_net_admin-eip'"
                                 " $(readlink -f $(which python))"])

    def _create_container(self):
        cont = Container()
        try:
            cont.check_permissions(getpass.getuser())
        except UserException as exc:
            print('Error:', exc, file=sys.stderr)
            sys.exit(1)
        try:
            print('Creating config file')
            conf = lxc_conf.LxcConf(Logger(Logger.LOG_NAME))
            conf.create()
        except Exception as exc:
            print("Error:", exc, file=sys.stderr)
            sys.exit(1)
        try:
            cont.create(self.args.create_container)
        except UserException as exc:
            print('Error:', exc, file=sys.stderr)
            sys.exit(1)
        print('Success: Container was created')

    def _config_file(self):
        dbase = Database()
        try:
            dbase.validate_config()
        except UserException as exc:
            print('Error:', exc.message, file=sys.stderr)
            sys.exit(1)
        print('Success: Config file validation passed')

    def launch(self):
        """Launch actions"""

        cmd = None
        # Determine which subcommand was specified
        try:
            if self.args.setup:
                cmd = argparse_gen.Cmd.SETUP.value
        except AttributeError:
            pass
        try:
            if self.args.config:
                cmd = argparse_gen.Cmd.CONFIG.value
        except AttributeError:
            pass
        try:
            if self.args.validate:
                cmd = argparse_gen.Cmd.VALIDATE.value
        except AttributeError:
            pass

        # Invoke subcommand method
        if cmd == argparse_gen.Cmd.SETUP.value:
            # self._check_root_user(cmd)
            if self.args.bridges:
                self._create_bridges()
        if cmd == argparse_gen.Cmd.CONFIG.value:
            self._check_non_root_user(cmd)
            if self.args.create_container:
                self._create_container()
            if self.args.mgmt_switches:
                self._config_mgmt_switches()
        if cmd == argparse_gen.Cmd.VALIDATE.value:
            self._check_non_root_user(cmd)
            if self.args.config_file:
                self._config_file()
            else:
                print('\n  Please specify an option for "gen {cmd}"\n'
                      '  Try "gen {cmd} -h" for help'.format(cmd=cmd))


if __name__ == '__main__':
    args = argparse_gen.get_parsed_args()
    GEN = Gen(args, Logger(
        Logger.LOG_NAME,
        args.log_level_file[0].upper(),
        args.log_level_print[0].upper()))
    GEN.launch()
