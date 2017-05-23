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
import xmlrpclib

from lib.logger import Logger

COBBLER_USER = 'cobbler'
COBBLER_PASS = 'cobbler'


class CobblerAddDistros(object):
    def __init__(self, log, path, name):
        name_list = [item.lower() for item in name.split('-')]

        if 'ubuntu' in name_list:
            breed = 'ubuntu'
            for item in name_list:
                if item == 'amd64':
                    arch = 'x86_64'
                    kernel = (
                        "%s/install/netboot/ubuntu-installer/amd64/linux" %
                        path)
                    initrd = (
                        "%s/install/netboot/ubuntu-installer/amd64/initrd.gz" %
                        path)
                elif item == 'ppc64el':
                    arch = 'ppc64le'
                    kernel = (
                        "%s/install/netboot/ubuntu-installer/ppc64el/vmlinux"
                        % path)
                    initrd = (
                        "%s/install/netboot/ubuntu-installer/ppc64el/initrd.gz"
                        % path)
                elif item.startswith('14.04'):
                    os_version = 'trusty'
                elif item.startswith('16.04'):
                    os_version = 'xenial'
            kernel_options = (
                "netcfg/dhcp_timeout=1024 "
                "netcfg/choose_interface=auto "
                "ipv6.disable=1")
            kickstart = "/var/lib/cobbler/kickstarts/%s.seed" % name

        elif ('centos' in name_list) or ('rhel' in name_list):
            breed = 'redhat'
            for item in name_list:
                if item == 'x86_64':
                    arch = 'x86_64'
                    kernel = "%s/images/pxeboot/vmlinuz" % path
                    initrd = "%s/images/pxeboot/initrd.img" % path
                elif item == 'ppc64le':
                    arch = 'ppc64le'
                    kernel = "%s/ppc/ppc64/vmlinuz" % path
                    initrd = "%s/ppc/ppc64/initrd.img" % path
                elif item.startswith('7'):
                    os_version = 'rhel7'
            kernel_options = "text"
            kickstart = "/var/lib/cobbler/kickstarts/%s.ks" % name

        elif 'introspection' in name_list:
            breed = 'redhat'  # use default since there is no "buildroot" breed
            os_version = ''
            arch = 'ppc64le'
            kernel = "%s/vmlinux" % path
            initrd = "%s/rootfs.cpio.gz" % path
            kernel_options = ''
            kickstart = ''

        cobbler_server = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
        token = cobbler_server.login(COBBLER_USER, COBBLER_PASS)

        new_distro_create = cobbler_server.new_distro(token)
        cobbler_server.modify_distro(
            new_distro_create,
            "name",
            name,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "arch",
            arch,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "kernel",
            kernel,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "initrd",
            initrd,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "breed",
            breed,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "os_version",
            os_version,
            token)
        cobbler_server.modify_distro(
            new_distro_create,
            "kernel_options",
            kernel_options,
            token)
        cobbler_server.save_distro(new_distro_create, token)

        log.info(
            "Cobbler Add Distro: name=%s, path=%s" %
            (name, path))

        new_profile_create = cobbler_server.new_profile(token)
        cobbler_server.modify_profile(
            new_profile_create,
            "name",
            name,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "distro",
            name,
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "enable_menu",
            "True",
            token)
        cobbler_server.modify_profile(
            new_profile_create,
            "kickstart",
            kickstart,
            token)
        cobbler_server.save_profile(new_profile_create, token)

        log.info(
            "Cobbler Add Profile: name=%s, distro=%s" %
            (name, name))

        cobbler_server.sync(token)
        log.info("Running Cobbler sync")


if __name__ == '__main__':
    """
    Arg1: path to install files
    Arg2: distro name
    Arg3: log level
    """
    LOG = Logger(__file__)

    ARGV_MAX = 4
    ARGV_COUNT = len(sys.argv)
    if ARGV_COUNT > ARGV_MAX:
        try:
            raise Exception()
        except:
            LOG.error('Invalid argument count')
            sys.exit(1)

    PATH = sys.argv[1]
    NAME = sys.argv[2]
    LOG.set_level(sys.argv[3])

    CobblerAddDistros(LOG, PATH, NAME)
