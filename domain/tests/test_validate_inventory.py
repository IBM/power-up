#!/usr/bin/env python
#
# Copyright 2016, IBM US, Inc.
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

import os
from os import path
import sys

import mock
import unittest

TOP_DIR = path.join(os.getcwd(), path.dirname(__file__), '..')
SCRIPT_DIR = 'scripts'
sys.path.append(path.join(TOP_DIR, SCRIPT_DIR))

import validate_inventory as test_mod


class TestValidateInventory(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_validate_reference_architecture(self):
        inv = {}
        # Test no ref arch
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_reference_architecture,
                          inv)

        # test no base
        inv['reference-architecture'] = ["these aren't the droids you're "
                                         "looking for"]
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_reference_architecture,
                          inv)

        # test dbaas w/o private compute base
        inv['reference-architecture'] = ['dbaas']
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_reference_architecture,
                          inv)

        # DBaaS, with swift
        inv['reference-architecture'] = ['swift', 'dbaas']
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_reference_architecture,
                          inv)

        # test min hardware, no base
        inv['reference-architecture'] = ['swift-minimum-hardware']
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_reference_architecture,
                          inv)

        # test min hardware, with swift
        inv['reference-architecture'] = ['swift-minimum-hardware', 'swift']
        test_mod.validate_reference_architecture(inv)

        # test min hardware, with private cloud
        inv['reference-architecture'] = ['swift-minimum-hardware',
                                         'swift',
                                         'private-compute-cloud']
        test_mod.validate_reference_architecture(inv)

        # test ceph standalone with private cloud
        inv['reference-architecture'] = ['ceph-standalone',
                                         'private-compute-cloud']
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_reference_architecture,
                          inv)

        # Test ceph standalone
        inv['reference-architecture'] = ['ceph-standalone']
        test_mod.validate_reference_architecture(inv)

        # Test base refs by themselves and together
        inv['reference-architecture'] = ['private-compute-cloud']
        test_mod.validate_reference_architecture(inv)

        inv['reference-architecture'] = ['private-compute-cloud', 'swift']
        test_mod.validate_reference_architecture(inv)

        inv['reference-architecture'] = ['private-compute-cloud', 'dbaas']
        test_mod.validate_reference_architecture(inv)

        # Test base refs by themselves and together
        inv['reference-architecture'] = ['swift']
        test_mod.validate_reference_architecture(inv)

    @mock.patch.object(test_mod, '_has_converged_metadata_object')
    @mock.patch.object(test_mod, '_has_separate_metadata_object')
    def test_validate_swift(self, separate, converged):

        # Test minimum hardware options
        inv = {'reference-architecture': ['swift', 'swift-minimum-hardware'],
               'node-templates': {'swift-proxy': {}}}
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_swift,
                          inv)

        converged.return_value = False
        inv['node-templates'].pop('swift-proxy')
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_swift,
                          inv)

        converged.return_value = True
        test_mod.validate_swift(inv)

        # Test non-minimum configs
        inv['node-templates'] = {'swift-proxy': {}}
        inv['reference-architecture'] = ['swift']
        converged.return_value = True
        separate.return_value = False
        test_mod.validate_swift(inv)

        converged.return_value = False
        separate.return_value = True
        test_mod.validate_swift(inv)

        # This one isn't really valid but the converged vs separate
        # method themselves check for this.
        converged.return_value = True
        separate.return_value = True
        test_mod.validate_swift(inv)

        converged.return_value = False
        separate.return_value = False
        self.assertRaises(test_mod.UnsupportedConfig,
                          test_mod.validate_swift,
                          inv)

    def test_has_converged_metadata_object(self):
        node_tmpl = {}
        inv = {'node-templates': node_tmpl}

        # Test good case first
        ds = {'account-ring-devices': [],
              'container-ring-devices': [],
              'object-ring-devices': []}
        node_tmpl['swift-object'] = {'domain-settings': ds}
        self.assertTrue(test_mod._has_converged_metadata_object(inv))

        # Test missing services
        ds = {'account-ring-devices': []}
        node_tmpl['swift-object'] = {'domain-settings': ds}
        self.assertFalse(test_mod._has_converged_metadata_object(inv))

        ds = {'account-ring-devices': [],
              'container-ring-devices': []}
        node_tmpl['swift-object'] = {'domain-settings': ds}
        self.assertFalse(test_mod._has_converged_metadata_object(inv))

        ds = {'account-ring-devices': [],
              'object-ring-devices': []}
        node_tmpl['swift-object'] = {'domain-settings': ds}
        self.assertFalse(test_mod._has_converged_metadata_object(inv))

        # Test swift-metadata in the mix
        ds = {'account-ring-devices': [],
              'container-ring-devices': [],
              'object-ring-devices': []}
        node_tmpl['swift-metadata'] = {'domain-settings': ds}
        self.assertFalse(test_mod._has_converged_metadata_object(inv))

    def test_has_separate_metadata_object(self):
        node_tmpl = {}
        inv = {'node-templates': node_tmpl}

        # Test good case first
        obj_ds = {'object-ring-devices': []}
        node_tmpl['swift-object'] = {'domain-settings': obj_ds}
        meta_ds = {'account-ring-devices': [],
                   'container-ring-devices': []}
        node_tmpl['swift-metadata'] = {'domain-settings': meta_ds}
        self.assertTrue(test_mod._has_separate_metadata_object(inv))

        # Test missing metadata services
        obj_ds = {'object-ring-devices': []}
        node_tmpl['swift-object'] = {'domain-settings': obj_ds}
        meta_ds = {'account-ring-devices': []}
        node_tmpl['swift-metadata'] = {'domain-settings': meta_ds}
        self.assertFalse(test_mod._has_separate_metadata_object(inv))

        # Test missing metadata template
        ds = {'account-ring-devices': [],
              'container-ring-devices': []}
        node_tmpl['swift-object'] = {'domain-settings': ds}
        self.assertFalse(test_mod._has_separate_metadata_object(inv))

        # Test missing swift-object template
        meta_ds = {'account-ring-devices': [],
                   'container-ring-devices': []}
        node_tmpl['swift-metadata'] = {'domain-settings': meta_ds}
        self.assertFalse(test_mod._has_separate_metadata_object(inv))

        # Test missing object ring
        obj_ds = {}
        node_tmpl['swift-object'] = {'domain-settings': obj_ds}
        meta_ds = {'account-ring-devices': [],
                   'container-ring-devices': []}
        node_tmpl['swift-metadata'] = {'domain-settings': meta_ds}
        self.assertFalse(test_mod._has_separate_metadata_object(inv))

    def test_validate_ops_mgr(self):
        # Test valid case
        net = 'openstack-mgmt'
        inventory = {'networks': {net: {}},
                     'node-templates': {'a': {'networks': [net]},
                                        'b': {'networks': [net]}}}
        test_mod.validate_ops_mgr(inventory)

        # Test missing network
        inventory['networks'].pop(net)
        self.assertRaisesRegexp(test_mod.UnsupportedConfig,
                                'required openstack-mgmt network',
                                test_mod.validate_ops_mgr,
                                inventory)
        # Test one template missing the network
        inventory['networks'][net] = {}
        inventory['node-templates']['a']['networks'].pop(0)
        expected_msg = 'The node template a is missing network openstack-mgmt'
        self.assertRaisesRegexp(test_mod.UnsupportedConfig,
                                expected_msg,
                                test_mod.validate_ops_mgr,
                                inventory)

    @mock.patch.object(test_mod, 'validate_ops_mgr')
    @mock.patch.object(test_mod, 'validate_ceph')
    @mock.patch.object(test_mod, 'validate_swift')
    @mock.patch.object(test_mod, 'validate_reference_architecture')
    @mock.patch.object(test_mod, '_load_yml')
    def test_validate(self, load, ra, swift, ceph, opsmgr):
        file_path = 'path'
        test_mod.validate(file_path)
        load.assert_called_once_with(file_path)
        ra.assert_called_once_with(load.return_value)
        swift.assert_called_once_with(load.return_value)
        ceph.assert_called_once_with(load.return_value)
        opsmgr.assert_called_once_with(load.return_value)
