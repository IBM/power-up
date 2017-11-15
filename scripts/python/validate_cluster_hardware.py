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
# import logging
from subprocess import Popen, PIPE
from pyroute2 import IPRoute, NetlinkError
from netaddr import IPNetwork
from pyghmi.ipmi import command
from pyghmi.exceptions import IpmiException

from lib.logger import Logger
from lib.exception import UserException
from lib.config import Config
from lib.ssh import SSH_Exception
from lib.switch_exception import SwitchException
from lib.switch import SwitchFactory

# offset relative to bridge address
NAME_SPACE_OFFSET_ADDR = 1


def main():
    log = Logger(Logger.LOG_NAME)
#    log = logging.getLogger()
    try:
        cfg = Config()
    except UserException as exc:
        log.error('Error - {}'.format(exc))
        sys.exit(1)
    try:
        log.set_level(cfg.get_globals_log_level())
    except:
        print('Unable to read log level from config file')
    try:
        log.set_display_level('info')
    except:
        print('Unable to set logging print level')

    val = ValidateClusterHardware(Logger(Logger.LOG_NAME))
    """Validate config"""
    if not val.validate_mgmt_switches():
        log.error('Failed validating cluster management switches')

    if not val.validate_data_switches():
        log.error('Failed validating cluster data switches')

    if not val.validate_ipmi():
        log.error('Failed cluster nodes IPMI validation')

    if not val.validate_pxe():
        log.error('Failed cluster nodes PXE validation')


def _sub_proc_exec(cmd):
    data = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = data.communicate()
    return stdout, stderr


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
#        self.log = logging.getLogger()
        self.log = Logger(Logger.LOG_NAME)
        self.log.set_level(Config().get_globals_log_level())
        self.addr = addr
        self.bridge = bridge
        self.vlan = bridge.split('-')[-1]
        self.name = name + self.vlan
        self.ip = IPRoute()
        self.log.info('Creating network namespace {}'.format(self.name))

        stdout, stderr = _sub_proc_exec('ip netns add {}'.format(self.name))
        if stderr:
            if 'File exists' in stderr:
                self.log.debug(stderr)
            else:
                self.log.error('Unable to create namespace')
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
        except NetlinkError:
            self.log.debug('Peer ifc already attached.')
        idx_br = self.ip.link_lookup(ifname=bridge)[0]
        self.idx_br_ifc = self.ip.link_lookup(ifname=self.br_ifc)[0]
        self.ip.link('set', index=self.idx_br_ifc, master=idx_br)

        # bring up the interfaces
        cmd = 'ip netns exec {} ip link set dev {} up'.format(
            self.name, self.peer_ifc)
        stdout, stderr = _sub_proc_exec(cmd)

        cmd = 'ip netns exec {} ip link set dev lo up'.format(self.name)
        stdout, stderr = _sub_proc_exec(cmd)

        cmd = 'ip netns exec {} ip addr add {} dev {} brd +' \
            .format(self.name, addr, self.peer_ifc)
        stdout, stderr = _sub_proc_exec(cmd)

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
        stdout, stderr = _sub_proc_exec(cmd)
        return stdout, stderr

    def _destroy_name_sp(self):
        self.ip.link('set', index=self.idx_br_ifc, state='down')
        self.ip.link('del', index=self.idx_br_ifc)
        self.ip.close()
        stdout, stderr = _sub_proc_exec('ip netns del {}'.format(self.name))


class ValidateClusterHardware(object):
    """Discover and validate cluster hardware

    Args:
        log (object): Log
    """

    def __init__(self, log):
        # self.log = logging.getLogger()
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

    def _verify_comm_ipmi(self, node_addr_list, cred_list):
        """ Attempts ipmi communication and mc reset cold against the list of
        nodes.  For each node try all available credentials.  If no credentials
        allow access, the node is not marked as succesful.
        Args:
            node_addr_list (list): list of ipv4 addresses for the discovered
            nodes. (ie those that previously fetched an address from the DHCP
             server.
            cred_list (list of lists): Each list item is a list containing the
            the userid, password and number of nodes for a node template.
        """
        tot = [cred_list[x][2] for x in range(len(cred_list))]
        tot = sum(tot)
        left = tot
        print()
        self.log.info("Validating IPMI communication and resetting BMC's")
        print()
        for node in node_addr_list:
            # resort list each time to maximize the probability of using the
            # correct credentials with minimum attempts
            cred_list.sort(key=lambda x: x[2], reverse=True)
            for j, creds in enumerate(cred_list):
                try:
                    bmc = command.Command(
                        node,
                        userid=creds[0],
                        password=creds[1])
                except IpmiException as exc:
                    if 'Incorrect password' in exc.message or \
                            'Unauthorized name' in exc.message:
                        pass
                    else:
                        self.log.error(exc.message)
                else:
                    self.log.debug(
                        node + ' power is ' + bmc.get_power()['powerstate'])
                    # reduce the number of nodes left to talk to with these
                    # credentials
                    cred_list[j][2] -= 1
                    left -= left
                    print('\r                                             ', end="")
                    print('\r{} of {} nodes communicating via IPMI'.
                          format(tot - left, tot), end="")
                    try:
                        bmc.reset_bmc()
                    except IpmiException as exc:
                        self.log.error('Failed attempting BMC reset on {}'.format(node))
                    break
        if left != 0:
            self.log.error('IPMI communication succesful with only {} of {} '
                           'nodes'.format(tot - left, tot))
            # raise UserException('IPMI communication succesful with only {} of'
            #                    ' {} nodes'.format(tot - left, tot))
        print()

    def validate_ipmi(self):
        self.log.info("\n________ Checking IPMI networks and client BMC's ________\n")
        ipmi_cnt, pxe_cnt = self._get_port_cnts()
        ipmi_addr, bridge_addr, ipmi_prefix, ipmi_vlan = self._get_network('ipmi')
        ipmi_network = ipmi_addr + '/' + str(ipmi_prefix)
        addr = IPNetwork(bridge_addr + '/' + str(ipmi_prefix))
        netmask = str(addr.netmask)
        ipmi_size = addr.size
        addr.value += NAME_SPACE_OFFSET_ADDR
        addr = str(addr)
        rc = True

        ipmi_ns = NetNameSpace('ipmi-ns-', 'br-ipmi-' + str(ipmi_vlan), addr)

        # setup DHCP, unless already running in namesapce
        # save start and end addr raw numeric values
        self.log.info('Installing DHCP server in network namespace')
        addr_st = self._add_offset_to_address(ipmi_network, 30)
        addr_end = self._add_offset_to_address(ipmi_network, 30 + ipmi_cnt + 2)

        cmd = 'dnsmasq --interface={} --dhcp-range={},{},{},3600' \
            .format(ipmi_ns._get_name_sp_ifc_name(),
                    addr_st, addr_end, netmask)

        dns_list, stderr = _sub_proc_exec('pgrep dnsmasq')
        dns_list = dns_list.splitlines()

        for pid in dns_list:
            ns_name, stderr = _sub_proc_exec('ip netns identify {}'.format(pid))
            if ipmi_ns._get_name_sp_name() in ns_name:
                print('DHCP already running in {}'.format(ns_name))
                break
        else:
            stdout, stderr = ipmi_ns._exec_cmd(cmd)
            print(stderr)

        # Scan up to 12 times. Delay 5 seconds between scans
        print('Scanning ipmi network')
        self.log.info('Pause 5 s between scans for cluster nodes to fetch'
                      ' DHCP addresses')
        for i in range(12):
            time.sleep(5)
            cmd = 'fping -r0 -a -g {} {}'.format(addr_st, addr_end)
            stdout, stderr = _sub_proc_exec(cmd)
            cnt = len(stdout.splitlines())
            print('{} of {} nodes have leases.'.format(cnt, ipmi_cnt))
            if cnt >= ipmi_cnt:
                break
            # After 8 tries, try expanding the search range to pick up nodes
            # which have a prexisting lease.
            if i == 9:
                self.log.info('Expanding IPMI search range')
                addr_end = self._add_offset_to_address(ipmi_network, ipmi_size - 2)
        node_list = stdout.splitlines()
        if ipmi_cnt != len(node_list):
            rc = False
            self.log.warning('Failed to validate expected number of nodes')

        # kill dnsmasq
        dns_list, stderr = _sub_proc_exec('pgrep dnsmasq')
        dns_list = dns_list.splitlines()

        for pid in dns_list:
            ns_name, stderr = _sub_proc_exec('ip netns identify ' + pid)
            if ipmi_ns._get_name_sp_name() in ns_name:
                self.log.debug('Killing dnsmasq {}'.format(pid))
                stdout, stderr = _sub_proc_exec('kill -15 ' + pid)

        cred_list = []
        port_tot = 0

        # create credentials list of lists
        for idx in self.cfg.yield_ntmpl_ind():
            cred_list.append([self.cfg.get_ntmpl_ipmi_userid(index=idx),
                             self.cfg.get_ntmpl_ipmi_password(index=idx)])
            for idx_ipmi in self.cfg.yield_ntmpl_phyintf_ipmi_ind(idx):
                port_cnt = self.cfg.get_ntmpl_phyintf_ipmi_pt_cnt(idx, idx_ipmi)
                port_tot += port_cnt
                cred_list[idx].append(port_cnt)

        if len(node_list) > 0 and len(cred_list) > 0:
            self._verify_comm_ipmi(node_list, cred_list)

        # Destroy the namespace
        self.log.debug('Destroying ipmi namespace')
        ipmi_ns._destroy_name_sp()

        self.log.info('Cluster nodes IPMI validation complete')
        return rc

    def validate_pxe(self):
        self.log.info("\n________ Checking PXE networks and client PXE ports ________\n")
        ipmi_cnt, pxe_cnt = self._get_port_cnts()
        pxe_addr, bridge_addr, pxe_prefix, pxe_vlan = self._get_network('pxe')
        pxe_network = pxe_addr + '/' + str(pxe_prefix)
        addr = IPNetwork(bridge_addr + '/' + str(pxe_prefix))
        netmask = str(addr.netmask)
        pxe_size = addr.size
        addr.value += NAME_SPACE_OFFSET_ADDR
        addr = str(addr)
        rc = True

        pxe_ns = NetNameSpace('pxe-ns-', 'br-pxe-' + str(pxe_vlan), addr)

        # setup DHCP, unless already running in namesapce
        # save start and end addr raw numeric values
        self.log.info('Installing DHCP server in network namespace')
        addr_st = self._add_offset_to_address(pxe_network, 30)
        addr_end = self._add_offset_to_address(pxe_network, 30 + pxe_cnt + 2)

        cmd = 'dnsmasq --interface={} --dhcp-range={},{},{},3600' \
            .format(pxe_ns._get_name_sp_ifc_name(),
                    addr_st, addr_end, netmask)

        dns_list, stderr = _sub_proc_exec('pgrep dnsmasq')
        dns_list = dns_list.splitlines()

        for pid in dns_list:
            ns_name, stderr = _sub_proc_exec('ip netns identify {}'.format(pid))
            if pxe_ns._get_name_sp_name() in ns_name:
                print('DHCP already running in {}'.format(ns_name))
                break
        else:
            stdout, stderr = pxe_ns._exec_cmd(cmd)
            print(stderr)

        # Scan up to 25 times. Delay 5 seconds between scans
        print('Scanning pxe network')
        self.log.info('Pause 5 s between scans for cluster nodes to fetch'
                      ' DHCP addresses')
        for i in range(25):
            time.sleep(5)
            cmd = 'fping -r0 -a -g {} {}'.format(addr_st, addr_end)
            stdout, stderr = _sub_proc_exec(cmd)
            cnt = len(stdout.splitlines())
            print('{} of {} nodes have leases.'.format(cnt, pxe_cnt))
            if cnt >= pxe_cnt:
                break
            # After 19 tries, try expanding the search range to pick up nodes
            # which have a prexisting lease.
            if i == 20:
                self.log.info('Expanding PXE search range')
                addr_end = self._add_offset_to_address(pxe_network, pxe_size - 2)
        node_list = stdout.splitlines()
        if pxe_cnt != len(node_list):
            rc = False
            self.log.warning('Failed to validate expected number of nodes')

        # kill dnsmasq
        dns_list, stderr = _sub_proc_exec('pgrep dnsmasq')
        dns_list = dns_list.splitlines()

        for pid in dns_list:
            ns_name, stderr = _sub_proc_exec('ip netns identify ' + pid)
            if pxe_ns._get_name_sp_name() in ns_name:
                self.log.debug('Killing dnsmasq {}'.format(pid))
                stdout, stderr = _sub_proc_exec('kill -15 ' + pid)

        # Destroy the namespace
        self.log.debug('Destroying ipmi namespace')
        pxe_ns._destroy_name_sp()

        self.log.info('Cluster nodes validation complete')
        return rc

    def _get_network(self, type_):
        """Returns details of a Genesis network.
        Args:
            type_ (str): Either 'pxe' or 'ipmi'
        Returns:
            network_addr: (str) ipv4 addr
            bridge_ipaddr: (str) ipv4 addr
            netprefix: (str)
            vlan: (str)
        """
        cfg = Config()
        types = cfg.get_depl_netw_client_type()
        bridge_ipaddr = cfg.get_depl_netw_client_brg_ip()
        vlan = cfg.get_depl_netw_client_vlan()
        netprefix = cfg.get_depl_netw_client_prefix()
        idx = types.index(type_)

        network = IPNetwork(bridge_ipaddr[idx] + '/' + str(netprefix[idx]))
        network_addr = str(network.network)
        return network_addr, bridge_ipaddr[idx], netprefix[idx], vlan[idx]

    def validate_data_switches(self):
        self.log.info('\n_______________ Verifying data switches _________________\n')
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
                        'Successfully pinged data switch \"%s\" at %s' %
                        (label, ip))
                else:
                    self.log.info(
                        'Failed to ping data switch \"%s\" at %s' % (label, ip))
                    rc = False
                try:
                    vlans = sw.show_vlans()
                    if vlans and len(vlans) > 1:
                        self.log.info(
                            'Successfully communicated with data switch \"%s\"'
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
        if rc:
            self.log.info(' OK - All data switches verified')
        return rc

    def validate_mgmt_switches(self):
        self.log.info('\n_____________ Verifying management switches _____________\n')
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
                self.log.info('Verifying switch communication on ip address:'
                              ' {}'.format(ip))
                sw = SwitchFactory.factory(
                    self.log,
                    switch_class,
                    ip,
                    userid,
                    password,
                    'active')
                if sw.is_pingable():
                    self.log.info(
                        'Successfully pinged management switch \"%s\" at %s' %
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
                        'Successfully communicated with management switch \"%s\"'
                        ' at %s' % (label, ip))
                else:
                    self.log.info(
                        'Failed to communicate with data switch \"%s\"'
                        'at %s' % (label, ip))
                    rc = False
        if rc:
            self.log.info(' OK - All management switches verified')
        return rc


if __name__ == '__main__':
    main()
