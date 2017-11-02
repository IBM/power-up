#!/usr/bin/env python
"""Container"""

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

import logging
import os.path
import re
import platform
import ConfigParser
from enum import Enum
from orderedattrdict import AttrDict
from Crypto.PublicKey import RSA

import lxc

from lib.logger import Logger
from lib.config import Config
from lib.exception import UserException
from lib.ssh import SSH_CONNECTION, SSH_Exception
from lib.genesis import GEN_PATH


class Container(object):
    """Container"""

    class Packages(Enum):
        DISTRO = 'pkgs-distro'
        PIP = 'pkgs-pip'
        VENV = 'pkgs-pip-venv'

    LXC_USERNET = '/etc/lxc/lxc-usernet'
    ARCHITECTURE = {u'x86_64': 'amd64', u'ppc64le': 'ppc64el'}
    RESOLV_CONF = '/etc/resolv.conf'
    RESOLV_CONF_BASE = '/etc/resolvconf/resolv.conf.d/base'
    RSA_BIT_LENGTH = 2048
    PRIVATE_SSH_KEY_FILE = os.path.expanduser('~/.ssh/gen')
    PUBLIC_SSH_KEY_FILE = os.path.expanduser('~/.ssh/gen.pub')
    PROJECT_PATH = '/opt/cluster-genesis'
    VENV_PATH = PROJECT_PATH + '/gen-venv'
    CONTAINER_INI = GEN_PATH + 'container.ini'
    CONTAINER_CONFIG_PATH = GEN_PATH + 'playbooks/lxc-conf.yml'

    def __init__(self):
        self.log = logging.getLogger(Logger.LOG_NAME)
        self.cfg = Config()
        self.rootfs = AttrDict(
            {'dist': 'ubuntu', 'release': 'trusty', 'arch': None})
        for key in self.ARCHITECTURE.keys():
            if key == platform.machine():
                self.rootfs.arch = self.ARCHITECTURE[key]
                break
        else:
            raise UserException('Unsupported hardware platform')

        self.cont = None
        self.cont_name = None

    def _lxc_run_command(self, cmd):
        if self.cont.attach_wait(lxc.attach_run_command, cmd):
            error = "Failed running '{}' in the container '{}'".format(
                ' '.join(cmd), self.cont_name)
            self.log.error(error)
            raise UserException(error)
        self.log.info(
            "Successfully ran '{}' in the container '{}'".format(
                ' '.join(cmd), self.cont_name))

    def check_permissions(self, user):
        # Enumerate LXC bridge
        entry = AttrDict({
            'user': user,
            'type': 'veth',
            'bridge': 'lxcbr0'})
        allows = []
        allows.append(entry.copy())

        # Enumerate management bridges
        for vlan in self.cfg.yield_depl_netw_mgmt_vlan():
            if vlan is not None:
                entry.bridge = 'br-mgmt-%d' % vlan
                allows.append(entry.copy())

        # Enumerate client bridges
        for index, vlan in enumerate(self.cfg.yield_depl_netw_client_vlan()):
            if vlan is not None:
                type_ = self.cfg.get_depl_netw_client_type(index)
                entry.bridge = 'br-%s-%d' % (type_, vlan)
                allows.append(entry.copy())

        # Check bridge permissions
        for line in open(self.LXC_USERNET, 'r'):
            match = re.search(
                r'^\s*(\w+)\s+(\w+)\s+([\w-]+)\s+(\d+)\s*$', line)
            if match is not None:
                allows[:] = [
                    allow for allow in allows
                    if not (
                        allow.user == match.group(1) and
                        allow.type == match.group(2) and
                        allow.bridge == match.group(3))]

        # If bridge permissions are missing
        if allows:
            msg = "Missing entries in '%s':" % self.LXC_USERNET
            for allow in allows:
                msg += ' (%s %s %s <number>)' % \
                    (allow.user, allow.type, allow.bridge)
            self.log.error(msg)
            raise Exception(msg)

        # Success
        self.log.info(
            "Unprivileged/non-root container bridge support found in '%s'" %
            self.LXC_USERNET)

    def create(self, name):
        self.cont = lxc.Container(name)
        self.cont_name = name

        # Check if container already exists
        if self.cont.defined:
            msg = "Container '%s' already exists" % name
            self.log.error(msg)
            raise Exception(msg)

        # Check if architecture is supported
        arch = platform.machine()
        if arch not in self.ARCHITECTURE.keys():
            msg = "Unsupported container architecture '%s'" % arch
            self.log.error(msg)
            raise Exception(msg)
        self.rootfs.arch = self.ARCHITECTURE[arch]

        # Create container
        if not self.cont.create('download', lxc.LXC_CREATE_QUIET, self.rootfs):
            msg = "Failed to create container '%s'" % name
            self.log.error(msg)
            raise Exception(msg)
        self.log.info("Created container '%s'" % name)

        # Start container
        if not self.cont.start():
            msg = "Failed to start container '%s'" % name
            self.log.error(msg)
            raise Exception(msg)
        self.log.info("Started container '%s'" % name)

        # Get nameservers from /etc/resolv.conf outside container
        nameservers = []
        try:
            with open(self.RESOLV_CONF, 'r') as resolv_conf:
                for line in resolv_conf:
                    if re.search(r'^nameserver', line):
                        nameservers.append(line.strip())
        except:
            msg = 'Failed to read: %s' % self.RESOLV_CONF
            self.log.error(msg)
            raise Exception(msg)

        # Update '/etc/resolv.conf' in container by updating
        # '/etc/resolvconf/resolv.conf.d/base'
        for line in nameservers:
            entry = 'a|%s' % line
            self._lxc_run_command(
                ['ex', '-sc', entry, '-cx', self.RESOLV_CONF_BASE])

        # Create user
        self._lxc_run_command(
            ['adduser', '--disabled-password', '--gecos', 'GECOS', 'deployer'])

        # Create '/root/.ssh' directory
        self._lxc_run_command(
            ['mkdir', '/root/.ssh'])

        # Create '/root/.ssh/authorized_keys' file
        self._lxc_run_command(
            ['touch', '/root/.ssh/authorized_keys'])

        # Change '/root/.ssh' permissions to 0700
        self._lxc_run_command(
            ['chmod', '700', '/root/.ssh'])

        # Change '/root/.ssh/authorized_keys' permissions to 0600
        self._lxc_run_command(
            ['chmod', '600', '/root/.ssh/authorized_keys'])

        key = RSA.generate(self.RSA_BIT_LENGTH)
        # Create private ssh key
        with open(self.PRIVATE_SSH_KEY_FILE, 'w') as ssh_key:
            ssh_key.write(key.exportKey())
        # Create public ssh key
        public_key = key.publickey().exportKey(format='OpenSSH')
        with open(self.PUBLIC_SSH_KEY_FILE, 'w') as ssh_key:
            ssh_key.write(public_key)

        # Add public ssh key to container
        self._lxc_run_command([
            'ex',
            '-sc', 'a|%s' % public_key,
            '-cx', '/root/.ssh/authorized_keys'])

        # Update/Upgrade container distro packages
        self._lxc_run_command(["sleep", "5"])
        self._lxc_run_command(["apt-get", "update"])
        self._lxc_run_command(["apt-get", "dist-upgrade", "-y"])

        # Read INI file
        ini = ConfigParser.SafeConfigParser(allow_no_value=True)
        try:
            ini.read(self.CONTAINER_INI)
        except ConfigParser.Error as exc:
            msg = exc.message.replace('\n', ' - ')
            self.log.error(msg)
            raise Exception(msg)

        # Install distro container packages
        if ini.has_section(self.Packages.DISTRO.value):
            cmd = ['apt-get', 'install', '-y']
            for pkg in ini.options(self.Packages.DISTRO.value):
                cmd.append(pkg)
            self._lxc_run_command(cmd)

        # Install pip container packages
        if ini.has_section(self.Packages.PIP.value):
            cmd = ['pip', 'install']
            for pkg in ini.options(self.Packages.PIP.value):
                cmd.append(pkg)
            self._lxc_run_command(cmd)

        # Create project
        self._lxc_run_command(
            ['mkdir', self.PROJECT_PATH])

        # Create virtual environment
        self._lxc_run_command([
            'virtualenv',
            '--no-wheel',
            '--system-site-packages',
            self.VENV_PATH])

        # Configure SSH connection
        cont_ipaddr = self.cont.get_ips(
            interface='eth0', family='inet', timeout=5)[0]
        try:
            ssh_cont = SSH_CONNECTION(
                cont_ipaddr,
                username='root',
                key_filename=self.PRIVATE_SSH_KEY_FILE)
        except SSH_Exception as exc:
            error = "SSH to container '{}' at '{}' failed".format(
                self.cont_name, cont_ipaddr)
            self.log.error(error)
            raise UserException(error)

        # Install pip venv container packages
        if ini.has_section(self.Packages.VENV.value):
            cmd = [
                'source', self.VENV_PATH + '/bin/activate',
                '&&', 'pip', 'install']
            for pkg, ver in ini.items(self.Packages.VENV.value):
                cmd.append('{}=={}'.format(pkg, ver))
            cmd.extend(['&&', 'deactivate'])
            status, stdout_, stderr_ = ssh_cont.send_cmd(' '.join(cmd))
            if status:
                error = 'Failed venv pip install'.format(self.VENV_PATH)
                self.log.error(error)
                raise UserException(error)
