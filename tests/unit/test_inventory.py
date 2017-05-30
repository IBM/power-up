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

import copy
import unittest

import mock
import inventory as test_mod

TEST_PKG_MOD = 'inventory'
DEBUG_TEST_CASES = False


class TestOSInterfacesInventory(unittest.TestCase):

    def setUp(self):
        if DEBUG_TEST_CASES:
            self.maxDiff = None

    def test_get_host_ip_to_node(self):
        source = {'nodes': {'type1': [{test_mod.HOST_IP_KEY: 'myIP',
                                       'otherkey': 'otherval1'},
                                      {test_mod.HOST_IP_KEY: 'myIP2',
                                       'otherkey': 'otherval2'},
                                      {test_mod.HOST_IP_KEY: 'myIP3',
                                       'otherkey': 'otherval3'},
                                      {'no_ip_key': 'something',
                                       'otherkey': 'otherval4'}],
                            'type2': [{test_mod.HOST_IP_KEY: 'myIP4',
                                       'otherkey': 'otherval5'},
                                      {test_mod.HOST_IP_KEY: 'myIP5',
                                       'otherkey': 'otherval6'},
                                      {test_mod.HOST_IP_KEY: 'myIP6',
                                       'otherkey': 'otherval7'},
                                      {'no_ip_key': 'something',
                                       'otherkey': 'otherval8'}]
                            }
                  }

        ret = test_mod.get_host_ip_to_node(source)
        expected = {'myIP': {test_mod.HOST_IP_KEY: 'myIP',
                             'otherkey': 'otherval1'},
                    'myIP2': {test_mod.HOST_IP_KEY: 'myIP2',
                              'otherkey': 'otherval2'},
                    'myIP3': {test_mod.HOST_IP_KEY: 'myIP3',
                              'otherkey': 'otherval3'},
                    'myIP4': {test_mod.HOST_IP_KEY: 'myIP4',
                              'otherkey': 'otherval5'},
                    'myIP5': {test_mod.HOST_IP_KEY: 'myIP5',
                              'otherkey': 'otherval6'},
                    'myIP6': {test_mod.HOST_IP_KEY: 'myIP6',
                              'otherkey': 'otherval7'}}
        self.assertDictEqual(ret, expected)

    def test_populate_hosts_and_groups(self):
        inventory = {'all': {'vars': {}},
                     '_meta': {'hostvars': {}}
                     }

        def gen_group(node_count):
            name = 'g%s' % node_count
            nodes = []
            for x in range(node_count):
                node_ip = 'n%s%s' % (name, x)
                nodes.append({test_mod.HOST_IP_KEY: node_ip})
            return {name: nodes}

        inventory_source = {'nodes': {},
                            'ansible_user': 'root',
                            'ansible_ssh_private_key_file': '~/.ssh/id_rsa'}
        inventory_source['nodes'].update(gen_group(3))
        inventory_source['nodes'].update(gen_group(5))
        inventory_source['nodes'].update(gen_group(1))
        inventory_source['node-templates'] = {'g3': {},
                                              'g5': {},
                                              'g1': {}}

        test_mod.populate_hosts_and_groups(inventory, inventory_source)
        children = inventory['all'].pop('children')
        self.assertItemsEqual(['g1', 'g3', 'g5'], children)
        expected = {
            'all': {
                'vars': {
                    'ansible_user': 'root',
                    'ansible_ssh_private_key_file': '~/.ssh/id_rsa'}},
            'g3': ['ng30', 'ng31', 'ng32'],
            'g5': ['ng50', 'ng51', 'ng52', 'ng53', 'ng54'],
            'g1': ['ng10'],
            '_meta': {
                'hostvars': {
                    'ng30': {}, 'ng31': {}, 'ng32': {},
                    'ng50': {}, 'ng51': {}, 'ng53': {},
                    'ng54': {}, 'ng10': {}, 'ng52': {}}}}
        self.assertDictEqual(inventory, expected)

        # Test with templates having a mix of roles
        inventory = {'all': {'vars': {}},
                     '_meta': {'hostvars': {}}
                     }
        inventory_source = {'nodes': {}}
        inventory_source['nodes'].update(gen_group(3))
        inventory_source['nodes'].update(gen_group(5))
        inventory_source['nodes'].update(gen_group(1))

        g3_roles = ['r1', 'r2', 'r3']
        g5_roles = ['r4', 'r5']
        g1_roles = ['r1', 'r4']
        inventory_source['node-templates'] = {'g3': {'roles': g3_roles},
                                              'g5': {'roles': g5_roles},
                                              'g1': {'roles': g1_roles}}
        test_mod.populate_hosts_and_groups(inventory, inventory_source)

        self.assertItemsEqual(inventory['r1'],
                              ['ng10', 'ng30', 'ng31', 'ng32'])
        self.assertItemsEqual(inventory['r2'],
                              ['ng30', 'ng31', 'ng32'])
        self.assertItemsEqual(inventory['r3'],
                              ['ng30', 'ng31', 'ng32'])
        self.assertItemsEqual(inventory['r4'],
                              ['ng10', 'ng50', 'ng51', 'ng52', 'ng53', 'ng54'])
        self.assertItemsEqual(inventory['r5'],
                              ['ng50', 'ng51', 'ng52', 'ng53', 'ng54'])
        children = inventory['all'].pop('children')
        self.assertItemsEqual(['g1', 'g3', 'g5', 'r1', 'r2', 'r3', 'r4', 'r5'],
                              children)

        # Test with a template having a role that matches its name
        inventory = {'all': {'vars': {}},
                     '_meta': {'hostvars': {}}
                     }
        inventory_source = {'nodes': {}}
        inventory_source['nodes'].update(gen_group(5))

        inventory_source['node-templates'] = {'g5': {'roles': ['g5']}}
        test_mod.populate_hosts_and_groups(inventory, inventory_source)
        self.assertItemsEqual(inventory['g5'],
                              ['ng50', 'ng51', 'ng52', 'ng53', 'ng54'])

        children = inventory['all'].pop('children')
        self.assertItemsEqual(['g5'], children)

    def test_sanitize_variable_name(self):
        name = 'hi-this-is-me'
        self.assertEqual('hi_this_is_me',
                         test_mod._sanitize_variable_name(name))

    def test_generic_variable_conversion(self):
        inventory = {'all': {'vars': {}},
                     '_meta': {'hostvars': {'ip1': {},
                                            'ip2': {},
                                            'ip3': {}}}
                     }
        nodes1 = [{test_mod.HOST_IP_KEY: 'ip1',
                   'some-key1': 'some-val1',
                   'somekey2': ['someval2']},
                  {test_mod.HOST_IP_KEY: 'ip2',
                   'some-key3': 'some-val3',
                   'somekey4': ['someval4']}]
        nodes2 = [{test_mod.HOST_IP_KEY: 'ip3',
                   'some-key4': 'some-val5',
                   'somekey6': ['someval6']}]
        inventory_source = {
            'global1': ['1', '2'],
            'global2': 'string-2',
            'global-3': {'a-1': 'b'},
            'nodes': {'group1': nodes1,
                      'group2': nodes2}}
        test_mod.generic_variable_conversion(inventory, inventory_source)
        san_ip = test_mod._sanitize_variable_name(test_mod.HOST_IP_KEY)
        expected = {'all': {'vars': {'global1': ['1', '2'],
                                     'global2': 'string-2',
                                     'global_3': {'a-1': 'b'}}},
                    '_meta': {'hostvars': {'ip1': {san_ip: 'ip1',
                                                   'some_key1': 'some-val1',
                                                   'somekey2': ['someval2']},
                                           'ip2': {san_ip: 'ip2',
                                                   'some_key3': 'some-val3',
                                                   'somekey4': ['someval4']},
                                           'ip3': {san_ip: 'ip3',
                                                   'some_key4': 'some-val5',
                                                   'somekey6': ['someval6']}}}}
        self.assertEqual(inventory, expected)

    def test_populate_network_variables(self):
        inventory = {'all': {'vars': {}},
                     '_meta': {'hostvars': {}}
                     }
        expected_output = copy.deepcopy(inventory)
        inv_src = {'networks': {'net1': {'addr': '10.5.1.5/22',
                                         'otherkey': 'otherval'},
                                'net2': {'addr': '0.0.0.0/1',
                                         'otherkey': 'otherval'},
                                'net3': {'otherkey': 'otherval'}}}
        test_mod.populate_network_variables(inventory, inv_src)
        nets = {'net1': {'addr': '10.5.1.5/22',
                         'network': '10.5.0.0',
                         'netmask': '255.255.252.0',
                         'otherkey': 'otherval'},
                'net2': {'addr': '0.0.0.0/1',
                         'otherkey': 'otherval'},
                'net3': {'otherkey': 'otherval'}}
        expected_output['all']['vars']['networks'] = nets
        self.assertDictEqual(inventory, expected_output)

    def test_populate_host_networks(self):
        # Set up test input
        inventory = {'_meta': {'hostvars': {}}}
        # net_list = ['net1', 'net2', 'net3', 'net4']
        nets = {'net1': {'addr': '1.1.1.0/24',
                         'network': '1.1.1.0',
                         'netmask': '255.255.255.0',
                         'method': 'static',
                         'otherkey': 'otherval'},
                'net2': {'addr': '0.0.0.0/1',
                         'method': 'manual',
                         'otherkey': 'otherval'},
                'net3': {'method': 'manual',
                         'otherkey': 'otherval'},
                'net4': {'method': 'manual',
                         'otherkey': 'otherval'}}
        inventory_source = {'networks': nets}
        ihv = inventory['_meta']['hostvars']
        for x in range(5):
            ihv['nodeIP%s' % x] = {}
        ip_to_node = {'nodeIP0': {'net1-addr': '1.1.1.1',
                                  'net2-addr': '2.2.2.1',
                                  'net4-addr': '4.4.4.1'},
                      'nodeIP1': {'net3-addr': '3.3.3.2'},
                      'nodeIP2': {'net1-addr': '1.1.1.3',
                                  'net2-addr': '',
                                  'net3-addr': '3.3.3.3'},
                      'nodeIP3': {'net1-addr': '1.1.1.4',
                                  'net3-addr': '3.3.3.4',
                                  'net4-addr': '4.4.4.4'},
                      'nodeIP4': {'net2-addr': '2.2.2.5',
                                  'net3-addr': '3.3.3.5'}
                      }

        expected_output = copy.deepcopy(inventory)
        hv = expected_output['_meta']['hostvars']
        hv['nodeIP0']['host_networks'] = {'net1': {'addr': '1.1.1.1'},
                                          'net2': {'addr': '2.2.2.1'},
                                          'net4': {'addr': '4.4.4.1'}}
        hv['nodeIP1']['host_networks'] = {'net3': {'addr': '3.3.3.2'}}
        hv['nodeIP2']['host_networks'] = {'net1': {'addr': '1.1.1.3'},
                                          'net2': {},
                                          'net3': {'addr': '3.3.3.3'}}
        hv['nodeIP3']['host_networks'] = {'net1': {'addr': '1.1.1.4'},
                                          'net3': {'addr': '3.3.3.4'},
                                          'net4': {'addr': '4.4.4.4'}}
        hv['nodeIP4']['host_networks'] = {'net2': {'addr': '2.2.2.5'},
                                          'net3': {'addr': '3.3.3.5'}}
        test_mod.populate_host_networks(
            inventory, inventory_source, ip_to_node)
        if DEBUG_TEST_CASES:
            import json
            print('Output %s' % json.dumps(inventory, indent=4))
            print('Expected_output %s' % json.dumps(expected_output, indent=4))
        self.assertDictEqual(inventory, expected_output)

        # Now test again with nodes not having any IP addresses on networks
        inventory = {'_meta': {'hostvars': {}}}
        ip_to_node = {'nodeIP0': {},
                      'nodeIP1': {},
                      'nodeIP2': {}}
        test_mod.populate_host_networks(
            inventory, inventory_source, ip_to_node)
        self.assertDictEqual(inventory, {'_meta': {'hostvars': {}}})

    @mock.patch(TEST_PKG_MOD + '.populate_name_interfaces')
    @mock.patch(TEST_PKG_MOD + '.populate_host_networks')
    @mock.patch(TEST_PKG_MOD + '.populate_network_variables')
    @mock.patch(TEST_PKG_MOD + '.populate_hosts_and_groups')
    @mock.patch(TEST_PKG_MOD + '.get_host_ip_to_node')
    @mock.patch(TEST_PKG_MOD + '.load_input_file')
    def test_generate_dynamic_inventory(self, load, get_host_ip_to_node,
                                        populate_hosts,
                                        populate_network_variables,
                                        populate_host_networks,
                                        populate_name_interfaces):
        ret = test_mod.generate_dynamic_inventory()
        load.assert_any_call()
        get_host_ip_to_node.assert_called_once_with(load.return_value)
        populate_hosts.assert_called_once_with(mock.ANY,
                                               load.return_value)
        populate_network_variables.assert_called_once_with(mock.ANY,
                                                           load.return_value)
        populate_name_interfaces.assert_called_once_with(
            mock.ANY, load.return_value, get_host_ip_to_node.return_value)
        self.assertTrue(populate_host_networks.called)
        expected_output = {'all': {'vars': {}},
                           '_meta': {'hostvars': {}}}
        self.assertDictEqual(ret, expected_output)

    def test_populate_name_interfaces(self):
        original_inventory = {'_meta': {'hostvars': {'nodeIP0': {},
                                                     'nodeIP1': {},
                                                     'nodeIP2': {}}}
                              }

        # Test when the templates do not have interfaces to name
        ip_to_node = {'nodeIP0': {'template': 'compute'},
                      'nodeIP1': {'template': 'controller'},
                      'nodeIP2': {'template': 'osd'}}

        source = {'node-templates': {
            'compute': {},
            'controller': {},
            'osd': {}}}
        inventory = copy.deepcopy(original_inventory)
        test_mod.populate_name_interfaces(inventory,
                                          source, ip_to_node)
        hv = inventory['_meta']['hostvars']
        self.assertDictEqual(hv, {'nodeIP0': {},
                                  'nodeIP1': {},
                                  'nodeIP2': {}})

        # Test when the MACs are not on the hosts yet
        source = {'node-templates': {
            'compute': {
                'name-interfaces': {'mac-key1': 'eth10',
                                    'mac-key2': 'eth20'}},
            'controller': {
                'name-interfaces': {'mac-key1': 'eth30',
                                    'mac-key2': 'eth40'}},
            'osd': {
                'name-interfaces': {'mac-key1': 'eth50',
                                    'mac-key2': 'eth60'}}}}

        inventory = copy.deepcopy(original_inventory)
        test_mod.populate_name_interfaces(inventory,
                                          source, ip_to_node)
        hv = inventory['_meta']['hostvars']
        self.assertDictEqual(hv, {'nodeIP0': {},
                                  'nodeIP1': {},
                                  'nodeIP2': {}})

        # Test once the mac have been added to the inventory
        ip_to_node = {'nodeIP0': {'mac-key1': 'key1val0',
                                  'mac-key2': 'key2val0',
                                  'template': 'compute'},
                      'nodeIP1': {'mac-key1': 'key1val1',
                                  'mac-key2': 'key2val1',
                                  'template': 'controller'},
                      'nodeIP2': {'mac-key1': 'key1val2',
                                  'mac-key2': 'key2val2',
                                  'template': 'osd'}}
        inventory = copy.deepcopy(original_inventory)
        test_mod.populate_name_interfaces(inventory,
                                          source, ip_to_node)
        hv = inventory['_meta']['hostvars']
        # Verify nodeIP0 vars
        ifs = {'eth10': 'key1val0',
               'eth20': 'key2val0'}
        self.assertEqual(hv['nodeIP0']['name_interfaces'], ifs)
        # Verify nodeIP1 vars
        ifs = {'eth30': 'key1val1',
               'eth40': 'key2val1'}
        self.assertEqual(hv['nodeIP1']['name_interfaces'], ifs)
        # Verify nodeIP2 vars
        ifs = {'eth50': 'key1val2',
               'eth60': 'key2val2'}
        self.assertEqual(hv['nodeIP2']['name_interfaces'], ifs)


if __name__ == "__main__":
    unittest.main()
