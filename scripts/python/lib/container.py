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
import lxc

from lib.logger import Logger
from lib.config import Config


class Container(object):
    """Container"""

    class Packages(Enum):
        DISTRO = 'pkgs-distro'
        PIP = 'pkgs-pip'
        VENV = 'pkgs-venv'

    LXC_USERNET = '/etc/lxc/lxc-usernet'
    ARCHITECTURE = {u'x86_64': 'amd64', u'ppc64le': 'ppc64el'}
    RESOLV_CONF = '/etc/resolv.conf'
    RESOLV_CONF_BASE = '/etc/resolvconf/resolv.conf.d/base'
    CONTAINER_INI = os.path.realpath('../../container.ini')

    def __init__(self):
        self.log = logging.getLogger(Logger.LOG_NAME)
        self.cfg = Config()
        self.rootfs = AttrDict(
            {'dist': 'ubuntu', 'release': 'trusty', 'arch': None})

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
                r'^\s*(r\w+)\s+(\w+)\s+([\w-]+)\s+(\d+)\s*$', line)
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
        cont = lxc.Container(name)

        # Check if container already exists
        if cont.defined:
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
        if not cont.create('download', lxc.LXC_CREATE_QUIET, self.rootfs):
            msg = "Failed to create container '%s'" % name
            self.log.error(msg)
            raise Exception(msg)
        self.log.info("Created container '%s'" % name)

        # Start container
        if not cont.start():
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

        # Update /etc/resolv.conf in container
        for line in nameservers:
            entry = 'a|%s' % line
            cont.attach_wait(
                lxc.attach_run_command,
                ['ex', '-sc', entry, '-cx', self.RESOLV_CONF_BASE])

        # Update/Upgrade container
        cont.attach_wait(lxc.attach_run_command, ["sleep", "5"])
        cont.attach_wait(lxc.attach_run_command, ["apt-get", "update"])
        cont.attach_wait(
            lxc.attach_run_command,
            ["apt-get", "dist-upgrade", "-y"])

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
            for pkg in ini.options(self.Packages.DISTRO.value):
                cont.attach_wait(
                    lxc.attach_run_command, ["apt-get", "install", "-y", pkg])

        # Install pip container packages

        # Install pip venv container packages

        # Create user
        cont.attach_wait(
            lxc.attach_run_command,
            ['adduser', '--disabled-password', '--gecos', 'GECOS', 'deployer'])
