#!/usr/bin/env python
"""Create lxc-conf.yml"""

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
import platform
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, \
    TemplateSyntaxError, TemplateAssertionError

from lib.logger import Logger
from lib.config import Config


class LxcConf(object):
    """Create lxc-conf.yml

    Args:
        log(object): log
    """

    TEMPLATE_DIR = os.path.realpath('../../playbooks/templates/localhost')
    TEMPLATE_FILE = 'lxc-conf.j2'
    LXC_CONF = os.path.realpath('../../playbooks/lxc-conf.yml')
    TYPE = 'type'
    VLAN = 'vlan'
    IPADDR = 'ipaddr'
    PREFIX = 'prefix'

    def __init__(self, log=None):
        self.cfg = Config()
        if log is not None:
            log.set_level(self.cfg.get_globals_log_level())
        self.log = log

    def create(self):
        """Create lxc-conf.yml"""

        env = Environment(loader=FileSystemLoader(self.TEMPLATE_DIR))
        try:
            template = env.get_template(self.TEMPLATE_FILE)
        except TemplateNotFound as exc:
            self.log.error('Template not found: %s' % exc.name)
            sys.exit(1)
        except TemplateAssertionError as exc:
            self.log.error('Template assertion error: %s in %s, line %d' % (
                exc.message, exc.filename, exc.lineno))
            sys.exit(1)
        except TemplateSyntaxError as exc:
            self.log.error('Template syntax error: %s in %s, line %d' % (
                exc.message, exc.filename, exc.lineno))
            sys.exit(1)

        nets = []
        for index, vlan in enumerate(self.cfg.yield_depl_netw_mgmt_vlan()):
            if vlan is not None:
                net = {}
                net[self.VLAN] = vlan
                net[self.IPADDR] = self.cfg.get_depl_netw_mgmt_cont_ip(index)
                net[self.PREFIX] = self.cfg.get_depl_netw_mgmt_prefix(index)
                nets.append(net)
        for index, type_ in enumerate(self.cfg.yield_depl_netw_client_type()):
            if type_ is not None:
                net = {}
                net[self.TYPE] = type_
                net[self.VLAN] = self.cfg.get_depl_netw_client_vlan(index)
                net[self.IPADDR] = self.cfg.get_depl_netw_client_cont_ip(index)
                net[self.PREFIX] = self.cfg.get_depl_netw_client_prefix(index)
                nets.append(net)
        distname, _, _ = platform.linux_distribution()

        try:
            with open(self.LXC_CONF, 'w') as lxc_conf:
                lxc_conf.write(template.render(
                    distribution=distname, networks=nets))
        except:
            self.log.error('Failed to create: %s' % self.LXC_CONF)
            sys.exit(1)

        self.log.info('Successfully created: %s' % self.LXC_CONF)


if __name__ == '__main__':
    LXC_CONF = LxcConf(Logger(Logger.LOG_NAME))
    LXC_CONF.create()
