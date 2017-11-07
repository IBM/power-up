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

import time
import sys
from subprocess import Popen, PIPE
from pyroute2 import IPRoute, netns, NetlinkError
from netaddr import IPNetwork

from lib.logger import Logger
from lib.exception import UserException
from lib.config import Config
from lib.ssh import SSH_Exception
from lib.switch_exception import SwitchException
from lib.switch import SwitchFactory

# offset relative to bridge address
NAME_SPACE_OFFSET_ADDR = 1


class NetNameSpace(object):
    """Instantiate a network namespace connected to a bridge

    Args:
        log (object): Log
    """
    def __init__(self, name, bridge, addr):
        """
        Args:
            name (str): namespace name
            bridge (str): name of bridge to attach to
            addr (str): cidr of namespace address
        """
        self.log = Logger(Logger.LOG_NAME)
        self.log.set_level(Config().get_globals_log_level())
        self.addr = addr
        self.bridge = bridge
        self.vlan = bridge.split('-')[-1]
        self.name = name + self.vlan
        self.ip = IPRoute()
        self.log.info('Creating network namespace {}'.format(self.name))

        try:
            netns.create(self.name)
        except OSError as exc:
            if 'File exists' not in exc:
                self.log.error('Error creating namespace {}'.format(self.name))
                sys.exit(1)
        self.br_ifc = 'veth-br-' + self.name.split('-')[0] + '-' + self.vlan
        self.peer_ifc = 'veth-' + self.name

        try:
            self.ip.link_create(
                ifname=self.br_ifc, peer=self.peer_ifc, kind='veth')
        except NetlinkError as exc:
            if 'File exists' not in exc:
                self.log.error('Failed creating veth pair. {}'.format(exc))
                sys.exit(1)

        try:
            # peer interface side disappears from host space once attached to
            # the namespace
            idx_ns_ifc = self.ip.link_lookup(ifname=self.peer_ifc)[0]
            self.ip.link('set', index=idx_ns_ifc, net_ns_fd=self.name)
        except IndexError:
            self.log.debug('Peer ifc already attached.')
        idx_br = self.ip.link_lookup(ifname=bridge)[0]
        self.idx_br_ifc = self.ip.link_lookup(ifname=self.br_ifc)[0]
        self.ip.link('set', index=self.idx_br_ifc, master=idx_br)

        # bring up the interfaces
        cmd = 'ip netns exec {} ip link set dev {} up'.format(
            self.name, self.peer_ifc)
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()

        cmd = 'ip netns exec {} ip link set dev lo up'.format(self.name)
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()

        cmd = 'ip netns exec {} ip addr add {} dev {} brd +' \
            .format(self.name, addr, self.peer_ifc)
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()

        # verify address setup
        # cmd = 'ip netns exec {} ip addr show'.format(self.name)
        # proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        # stdout, stderr = proc.communicate()

        self.ip.link('set', index=self.idx_br_ifc, state='up')

    def _get_name_sp_ifc_name(self):
        return self.peer_ifc

    def _get_name_sp_name(self):
        return self.name

    def _get_name_sp_addr(self):
        return self.addr

    def _exec_cmd(self, cmd):
        """Execute a command in the namespace

        Args:
            log (object): Log
            cmd (string)
        """
        cmd = 'ip netns exec {} {}'.format(self.name, cmd)
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        return stdout, stderr

    def _destroy_name_sp(self):
        self.ip.link('del', index=self.idx_br_ifc)
        netns.remove(self.name)


class ValidateClusterHardware(object):
    """Discover and validate cluster hardware

    Args:
        log (object): Log
    """

    def __init__(self, log=None):
        if log is not None:
            try:
                self.cfg = Config()
            except UserException as exc:
                print(exc)
                sys.exit(1)
            try:
                log.set_level(self.cfg.get_globals_log_level())
            except:
                print('Unable to read log level from config file')
            try:
                log.set_display_level('info')
            except:
                print('Unable to set logging print level')
            self.log = log

    def validate_cluster(self):
        """Validate config"""
        self.log.info('\n_____________ Verifying management switches _____________\n')
        if self._validate_mgmt_switches():
            self.log.info(' OK - All management switches verified')
        else:
            self.log.error('Failed validating cluster management switches')

        self.log.info('\n_______________ Verifying data switches _________________\n')
        if self._validate_data_switches():
            self.log.info('OK - All data switches verified')
        else:
            self.log.error('Failed validating cluster data switches')

        self.log.info("\n________ Checking IPMI networks and client BMC's ________\n")
        if self.validate_ipmi():
            self.log.info('Cluster nodes validation complete')

    def _add_offset_to_address(self, addr, offset):
        """calculates an address with an offset added.
        Args:
            addr (str): ipv4 or cidr representation of address
            offset (int): integer offset
        Returns:
            addr_.ip (str) address in ipv4 representation
        """
        addr_ = IPNetwork(addr)
        addr_.value += offset
        return str(addr_.ip)

    def _get_port_cnts(self):
        labels = self.cfg.get_sw_mgmt_label()
        ipmi_cnt = 0
        pxe_cnt = 0

        for label in labels:
            ipmi_cnt += len(self.cfg.get_client_switch_ports(label, 'ipmi'))
            pxe_cnt += len(self.cfg.get_client_switch_ports(label, 'pxe'))
        return ipmi_cnt, pxe_cnt

    def validate_ipmi(self):
        ipmi_cnt, pxe_cnt = self._get_port_cnts()

        ipmi_addr, bridge_addr, ipmi_prefix, ipmi_vlan = self._get_ipmi_network()
        ipmi_network = ipmi_addr + '/' + str(ipmi_prefix)
#        print('IPMI network: {}'.format(ipmi_network))
#        print('Preliminary scan of IPMI network')
#        data = Popen(['fping', '-r0', '-a', '-g', ipmi_network], stdout=PIPE, stderr=PIPE)
#        stdout, stderr = data.communicate()
#        print(stdout)
        addr = IPNetwork(bridge_addr + '/' + str(ipmi_prefix))
        netmask = str(addr.netmask)
        addr.value += NAME_SPACE_OFFSET_ADDR
        addr = str(addr)
        ipmi_ns = NetNameSpace('ipmi-ns-', 'br-ipmi-' + str(ipmi_vlan), addr)

        # setup DHCP, unless already running in namesapce
        # save start and end addr raw numeric values
        self.log.info('Installing DHCP server in network namespace')
        addr_st = self._add_offset_to_address(ipmi_network, 100)
        addr_end = self._add_offset_to_address(ipmi_network, 100 + ipmi_cnt + 2)

        cmd = 'dnsmasq --interface={} --dhcp-range={},{},{},300' \
            .format(ipmi_ns._get_name_sp_ifc_name(),
                    addr_st, addr_end, netmask)

        data = Popen(['pgrep', 'dnsmasq'], stdout=PIPE, stderr=PIPE)
        dns_list, stderr = data.communicate()
        dns_list = dns_list.splitlines()

        for pid in dns_list:
            data = Popen(['ip', 'netns', 'identify', pid], stdout=PIPE, stderr=PIPE)
            ns_name, stderr = data.communicate()
            if ipmi_ns._get_name_sp_name() in ns_name:
                print('DHCP already running in {}'.format(ns_name))
                break
        else:
            stdout, stderr = ipmi_ns._exec_cmd(cmd)
            print(stderr)

        # Scan up to 12 times. Delay 5 seconds between scans
        print('Scanning ipmi network')
        self.log.info('Pause 5 s between scans for cluster nodes to fetch DHCP addresses')
        for i in range(12):
            time.sleep(5)
            data = Popen(['fping', '-r0', '-a', '-g', addr_st, addr_end],
                         stdout=PIPE, stderr=PIPE)
            stdout, stderr = data.communicate()
            cnt = len(stdout.splitlines())
            print('{} of {} nodes have leases.'.format(cnt, ipmi_cnt))
            if cnt >= ipmi_cnt:
                break

        # kill dnsmasq
        data = Popen(['pgrep', 'dnsmasq'], stdout=PIPE, stderr=PIPE)
        dns_list, stderr = data.communicate()
        dns_list = dns_list.splitlines()

        for pid in dns_list:
            data = Popen(['ip', 'netns', 'identify', pid],
                         stdout=PIPE, stderr=PIPE)
            ns_name, stderr = data.communicate()
            if ipmi_ns._get_name_sp_name() in ns_name:
                self.log.debug('Killing dnsmasq {}'.format(pid))
                data = Popen(['kill', '-15', pid], stdout=PIPE, stderr=PIPE)
                stdout, stderr = data.communicate()

        self.log.debug('Destroying ipmi namespace')
        ipmi_ns._destroy_name_sp()
        return True

    def _get_ipmi_network(self):
        """Returns details of the ipmi network
        Returns:
            network_addr: (str) ipv4 addr
            bridge_ipaddr: (str) ipv4 addr
            netprefix: (str)
            vlan: (str)
        """
        cfg = Config()
        type_ = cfg.get_depl_netw_client_type()
        bridge_ipaddr = cfg.get_depl_netw_client_brg_ip()
        vlan = cfg.get_depl_netw_client_vlan()
        netprefix = cfg.get_depl_netw_client_prefix()
        idx = type_.index('ipmi')

        network = IPNetwork(bridge_ipaddr[idx] + '/' + str(netprefix[idx]))
        network_addr = str(network.network)
        return network_addr, bridge_ipaddr[idx], netprefix[idx], vlan[idx]

    def _validate_data_switches(self):
        self.log.debug('---------- validate_data_switches --------------')
        cfg = Config()

        sw_cnt = cfg.get_sw_data_cnt()
        self.log.info('Number of data switches defined in config file: {}'.
                      format(sw_cnt))

        for index, switch_label in enumerate(cfg.yield_sw_data_label()):

            label = cfg.get_sw_data_label(index)
            self.log.debug('switch_label: {}'.format(switch_label))

            switch_class = cfg.get_sw_data_class(index)
            if not switch_class:
                self.log.error('No switch class found')
                return False
            userid = None
            password = None
            rc = True

            try:
                userid = cfg.get_sw_data_userid(index)
            except AttributeError:
                self.log.info('Passive switch mode specified')
                return True

            try:
                password = cfg.get_sw_data_password(index)
            except AttributeError:
                try:
                    cfg.get_sw_data_ssh_key(index)
                except AttributeError:
                    return True
                else:
                    self.log.error(
                        'Switch authentication via ssh keys not yet supported')
                    return False
            # Verify communication on each defined interface
            for ip in cfg.yield_sw_data_interfaces_ip(index):
                self.log.info('Verifying switch communication on ip'
                              ' address: {}'.format(ip))
                sw = SwitchFactory.factory(
                    self.log,
                    switch_class,
                    ip,
                    userid,
                    password,
                    'active')
                if sw.is_pingable():
                    self.log.info(
                        'Sucessfully pinged data switch \"%s\" at %s' %
                        (label, ip))
                else:
                    self.log.info(
                        'Failed to ping data switch \"%s\" at %s' % (label, ip))
                    rc = False
                try:
                    vlans = sw.show_vlans()
                    if vlans and len(vlans) > 1:
                        self.log.info(
                            'Sucessfully communicated with data switch \"%s\"'
                            ' at %s' % (label, ip))
                    else:
                        self.log.info(
                            'Failed to communicate with data switch \"%s\"'
                            'at %s' % (label, ip))
                        rc = False
                except (SwitchException, SSH_Exception):
                    self.log.error('Failed communicating with data switch'
                                   ' at address {}'.format(ip))
                    rc = False
        return rc

    def _validate_mgmt_switches(self):
        self.log.debug('-------------- validate_mgmt_switches --------------')
        cfg = Config()

        sw_cnt = cfg.get_sw_mgmt_cnt()
        self.log.info('Number of management switches defined in config file: {}'.
                      format(sw_cnt))

        for index, switch_label in enumerate(cfg.yield_sw_mgmt_label()):

            label = cfg.get_sw_mgmt_label(index)
            self.log.debug('switch_label: {}'.format(switch_label))

            switch_class = cfg.get_sw_mgmt_class(index)
            if not switch_class:
                self.log.error('No switch class found')
                return False
            userid = None
            password = None
            rc = True

            try:
                userid = cfg.get_sw_mgmt_userid(index)
            except AttributeError:
                self.log.info('Passive switch mode specified')
                return rc

            try:
                password = cfg.get_sw_mgmt_password(index)
            except AttributeError:
                try:
                    cfg.get_sw_mgmt_ssh_key(index)
                except AttributeError:
                    return rc
                else:
                    self.log.error(
                        'Switch authentication via ssh keys not yet supported')
                    rc = False
            # Verify communication on each defined interface
            for ip in cfg.yield_sw_mgmt_interfaces_ip(index):
                self.log.info('Verifying switch communication on ip address: {}'.
                              format(ip))
                sw = SwitchFactory.factory(
                    self.log,
                    switch_class,
                    ip,
                    userid,
                    password,
                    'active')
                if sw.is_pingable():
                    self.log.info(
                        'Sucessfully pinged management switch \"%s\" at %s' %
                        (label, ip))
                else:
                    self.log.info(
                        'Failed to ping management switch \"%s\" at %s' %
                        (label, ip))
                    rc = False
                try:
                    vlans = sw.show_vlans()
                except (SwitchException, SSH_Exception):
                    self.log.error('Failed communicating with management switch'
                                   ' at address {}'.format(ip))
                    rc = False

                if vlans and len(vlans) > 1:
                    self.log.info(
                        'Sucessfully communicated with management switch \"%s\"'
                        ' at %s' % (label, ip))
                else:
                    self.log.info(
                        'Failed to communicate with data switch \"%s\"'
                        'at %s' % (label, ip))
                    rc = False
        return rc


if __name__ == '__main__':
    VAL = ValidateClusterHardware(Logger(Logger.LOG_NAME))
    VAL.validate_cluster()
