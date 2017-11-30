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

import os
import sys
import getpass

import enable_deployer_networks
import validate_cluster_hardware
import configure_mgmt_switches
import download_os_images
import lxc_conf
import lib.argparse_gen as argparse_gen
import lib.logger as logger
import lib.genesis as gen
from lib.db import Database
from lib.exception import UserException


class Gen(object):
    """Cluster Genesis 'gen' command

    Args:
        log(object): log
    """

    ROOTUSER = 'root'

    def __init__(self, args):
        self.args = args

    def _check_root_user(self, cmd):
        if getpass.getuser() != self.ROOTUSER:
            print(
                "Fail: '%s %s ...' should be run as root" %
                (sys.argv[0], cmd),
                file=sys.stderr)
            sys.exit(1)

    def _check_non_root_user(self, cmd):
        if getpass.getuser() == self.ROOTUSER:
            print(
                "Fail: '%s %s ...' should not be run as root" %
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
        enable_deployer_networks.enable_deployer_network()

    def _create_container(self):
        from lib.container import Container

        cont = Container(self.args.create_container)
        try:
            cont.check_permissions(getpass.getuser())
        except UserException as exc:
            print('Fail:', exc, file=sys.stderr)
            sys.exit(1)
        try:
            conf = lxc_conf.LxcConf()
            conf.create()
        except Exception as exc:
            print("Fail:", exc, file=sys.stderr)
            sys.exit(1)
        try:
            cont.create()
        except UserException as exc:
            print('Fail:', exc, file=sys.stderr)
            sys.exit(1)
        print('Success: Created container')

    def _config_file(self):
        dbase = Database()
        try:
            dbase.validate_config(self.args.config_file)
        except UserException as exc:
            print('Fail:', exc.message, file=sys.stderr)
            sys.exit(1)
        print('Success: Config file validation passed')

    def _cluster_hardware(self):
        val = validate_cluster_hardware.ValidateClusterHardware()
        rc1 = val.validate_mgmt_switches()
        rc2 = val.validate_data_switches()
        val.validate_ipmi()
        val.validate_pxe()
        if not rc1 and rc2:
            self.log.critical('Failed switch validation')
            sys.exit(1)

    def _create_inventory(self):
        from lib.container import Container

        cont = Container(self.args.create_inventory)
        cmd = []
        cmd.append(gen.get_container_venv_python_exe())
        cmd.append(os.path.join(
            gen.get_container_python_path(), 'inv_create.py'))
        try:
            cont.run_command(cmd)
        except UserException as exc:
            print('Fail:', exc.message, file=sys.stderr)
            sys.exit(1)
        print('Success: Created inventory file')

    def _install_cobbler(self):
        from lib.container import Container

        cont = Container(self.args.install_cobbler)
        cmd = []
        cmd.append(gen.get_container_venv_python_exe())
        cmd.append(os.path.join(
            gen.get_container_python_path(), 'cobbler_install.py'))
        try:
            cont.run_command(cmd)
        except UserException as exc:
            print('Fail:', exc.message, file=sys.stderr)
            sys.exit(1)
        print('Success: Cobbler installed')

    def _download_os_images(self):
        from lib.container import Container

        try:
            download_os_images.download_os_images()
        except UserException as exc:
            print('Fail:', exc.message, file=sys.stderr)
            sys.exit(1)

        cont = Container(self.args.download_os_images)
        ssh = cont.open_ssh()
        sftp = cont.open_sftp(ssh)
        try:
            cont.copy_dir_to_container(sftp, cont.depl_os_images_path)
        except UserException as exc:
            print('Fail:', exc.message, file=sys.stderr)
            sys.exit(1)
        print('Success: OS images downloaded and copied into container')

    def _inv_add_ports_ipmi(self):
        dhcp_lease_file = '/var/lib/misc/dnsmasq.leases'
        from lib.container import Container

        cont = Container(self.args.inv_add_ports_ipmi)
        cmd = []
        cmd.append(gen.get_container_venv_python_exe())
        cmd.append(os.path.join(
            gen.get_container_python_path(), 'inv_add_ports.py'))
        cmd.append(dhcp_lease_file)
        cmd.append('ipmi')
        try:
            cont.run_command(cmd)
        except UserException as exc:
            print('Fail:', exc.message, file=sys.stderr)
            sys.exit(1)
        print('IPMI ports added to inventory')

    def _inv_add_ports_pxe(self):
        dhcp_lease_file = '/var/lib/misc/dnsmasq.leases'
        from lib.container import Container

        cont = Container(self.args.inv_add_ports_pxe)
        cmd = []
        cmd.append(gen.get_container_venv_python_exe())
        cmd.append(os.path.join(
            gen.get_container_python_path(), 'inv_add_ports.py'))
        cmd.append(dhcp_lease_file)
        cmd.append('pxe')
        try:
            cont.run_command(cmd)
        except UserException as exc:
            print('Fail:', exc.message, file=sys.stderr)
            sys.exit(1)
        print('PXE ports added to inventory')

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
        try:
            if self.args.deploy:
                cmd = argparse_gen.Cmd.DEPLOY.value
        except AttributeError:
            pass

        # Invoke subcommand method
        if cmd == argparse_gen.Cmd.SETUP.value:
            if gen.is_container():
                print(
                    'Fail: Invalid subcommand in container', file=sys.stderr)
                sys.exit(1)
            self._check_root_user(cmd)
            if self.args.bridges:
                self._create_bridges()

        if cmd == argparse_gen.Cmd.CONFIG.value:
            if gen.is_container():
                print(
                    'Fail: Invalid subcommand in container', file=sys.stderr)
                sys.exit(1)
            self._check_non_root_user(cmd)
            if argparse_gen.is_arg_present(self.args.create_container):
                self._create_container()
            if self.args.mgmt_switches:
                self._config_mgmt_switches()

        if cmd == argparse_gen.Cmd.VALIDATE.value:
            if argparse_gen.is_arg_present(self.args.config_file):
                self._check_non_root_user(cmd)
                self._config_file()
            elif self.args.cluster_hardware:
                self._check_root_user(cmd)
                self._cluster_hardware()

        if cmd == argparse_gen.Cmd.DEPLOY.value:
            if gen.is_container():
                print(
                    'Fail: Invalid subcommand in container', file=sys.stderr)
                sys.exit(1)
            if argparse_gen.is_arg_present(self.args.create_inventory):
                self._create_inventory()
            if argparse_gen.is_arg_present(self.args.install_cobbler):
                self._install_cobbler()
            if argparse_gen.is_arg_present(self.args.download_os_images):
                self._download_os_images()
            if argparse_gen.is_arg_present(self.args.inv_add_ports_ipmi):
                self._inv_add_ports_ipmi()
            if argparse_gen.is_arg_present(self.args.inv_add_ports_pxe):
                self._inv_add_ports_pxe()


if __name__ == '__main__':
    args = argparse_gen.get_parsed_args()
    logger.create(
        args.log_level_file[0],
        args.log_level_print[0])
    GEN = Gen(args)
    GEN.launch()
