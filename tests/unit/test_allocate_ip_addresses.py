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

import types
import collections
import unittest

import allocate_ip_addresses

DEBUG_TEST_CASES = False


class TestAllocateIPAddresses(unittest.TestCase):

    def setUp(self):
        if DEBUG_TEST_CASES:
            self.maxDiff = None

    def test_get_networks(self):
        inv = {'networks': {'net1': {'method': 'static',
                                     'addr': '0.0.0.0/1'},
                            'net2': {'method': 'dhcp',
                                     'addr': '1.2.3.0/22'},
                            'net3': {'method': 'manual'},
                            'net4': {'method': 'static',
                                     'addr': '10.1.1.0/24',
                                     'gateway': '10.1.1.1',
                                     'dns-nameservers': '10.1.1.3'},
                            'net5': {'method': 'static',
                                     'addr': '10.1.1.0/24',
                                     'gateway': '10.1.1.1',
                                     'dns-nameservers': ['10.1.1.3',
                                                         '10.1.1.4']},
                            'net6': {'method': 'static',
                                     'addr': '10.0.1.0/24',
                                     'available-ips':
                                         ['10.0.1.20',
                                          '10.0.1.35',
                                          '10.0.1.106 10.0.1.110',
                                          '10.0.1.115'],
                                     'gateway': '10.0.1.1',
                                     'dns-nameservers': '10.0.1.2'}}}
        available_network_ips = allocate_ip_addresses.load_network_ips(inv)
        nets = allocate_ip_addresses.get_networks(inv, available_network_ips)
        self.assertTrue('net1' in nets.keys())
        self.assertEqual(nets['net1']['exclude'], [None])
        self.assertEqual(str(nets['net1']['net'].network), '0.0.0.0')
        self.assertTrue(isinstance(nets['net1']['ip_iterator'],
                                   types.GeneratorType))

        self.assertFalse('net2' in nets.keys())

        self.assertTrue('net3' in nets.keys())
        self.assertFalse('exclude' in nets['net3'])
        self.assertFalse('net' in nets['net3'])

        self.assertTrue('net4' in nets.keys())
        self.assertEqual(nets['net4']['exclude'], ['10.1.1.1', '10.1.1.3'])
        self.assertEqual(str(nets['net4']['net'].network), '10.1.1.0')
        self.assertTrue(isinstance(nets['net4']['ip_iterator'],
                                   types.GeneratorType))

        self.assertTrue('net5' in nets.keys())
        self.assertEqual(nets['net5']['exclude'], ['10.1.1.1', '10.1.1.3',
                                                   '10.1.1.4'])
        self.assertEqual(str(nets['net5']['net'].network), '10.1.1.0')
        self.assertTrue(isinstance(nets['net5']['ip_iterator'],
                                   types.GeneratorType))

        self.assertTrue('net6' in nets.keys())
        self.assertEqual(nets['net6']['exclude'], ['10.0.1.1', '10.0.1.2'])
        self.assertEqual(str(nets['net6']['net'].network), '10.0.1.0')
        self.assertTrue(isinstance(nets['net6']['ip_iterator'],
                                   collections.Iterable))

    def test_allocate_ips_to_nodes_existing_ip(self):
        # Test the allocate code when a node already has an IP
        # on a network.
        inv = {'networks': {'net4': {'method': 'static',
                                     'addr': '10.1.1.0/24',
                                     'gateway': '10.1.1.1',
                                     'dns-nameservers': '10.1.1.3'},
                            'net5': {'method': 'static',
                                     'addr': '10.2.1.0/24',
                                     'gateway': '10.2.1.1',
                                     'dns-nameservers': ['10.2.1.3',
                                                         '10.2.1.4']},
                            'net6': {'method': 'static',
                                     'addr': '10.0.1.0/24',
                                     'available-ips':
                                         ['10.0.1.20',
                                          '10.0.1.35',
                                          '10.0.1.105 10.0.1.110',
                                          '10.0.1.115'],
                                     'gateway': '10.0.1.1',
                                     'dns-nameservers': '10.0.1.2'}}}
        templates = {'controller': {'networks': ['net4', 'net5', 'net6']}}

        nodes = {'controllers': [{'template': 'controller',
                                  'net4-addr': '10.1.1.15'},
                                 {'template': 'controller',
                                  'net5-addr': '10.2.1.16'},
                                 {'template': 'controller',
                                  'net6-addr': '10.0.1.17'},
                                 {'template': 'controller'}]}
        inv['nodes'] = nodes
        inv['node-templates'] = templates

        available_network_ips = allocate_ip_addresses.load_network_ips(inv)
        nets = allocate_ip_addresses.get_networks(inv, available_network_ips)
        allocate_ip_addresses.allocate_ips_to_nodes(inv, nets)
        expected_nodes = {'controllers': [{'template': 'controller',
                                           'net4-addr': '10.1.1.15',
                                           'net5-addr': '10.2.1.2',
                                           'net6-addr': '10.0.1.20'},
                                          {'template': 'controller',
                                           'net4-addr': '10.1.1.2',
                                           'net5-addr': '10.2.1.16',
                                           'net6-addr': '10.0.1.35'},
                                          {'template': 'controller',
                                           'net4-addr': '10.1.1.4',
                                           'net5-addr': '10.2.1.5',
                                           'net6-addr': '10.0.1.17'},
                                          {'template': 'controller',
                                           'net4-addr': '10.1.1.5',
                                           'net5-addr': '10.2.1.6',
                                           'net6-addr': '10.0.1.105'}]}
        if DEBUG_TEST_CASES:
            import json
            print('Output %s' % json.dumps(inv, indent=4))
            print('Expected_output %s' % json.dumps(expected_nodes, indent=4))
            self.maxDiff = None
        self.assertEqual(inv['nodes'], expected_nodes)


if __name__ == "__main__":
    unittest.main()
