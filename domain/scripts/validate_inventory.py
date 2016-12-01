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

import argparse
import sys
import yaml

SWIFT = 'swift'
SWIFT_MIN = 'swift-minimum-hardware'
CEPH = 'ceph-standalone'
DBAAS = 'dbaas'
COMPUTE = 'private-compute-cloud'
BASE_ARCHS = {SWIFT, COMPUTE, CEPH}


class UnsupportedConfig(Exception):
    pass


def validate(file_path):
    try:
        inventory = _load_yml(file_path)
        validate_reference_architecture(inventory)
        validate_swift(inventory)
        validate_ceph(inventory)
        validate_ops_mgr(inventory)
    except Exception as ex:
        print ex
        sys.exit(1)


def validate_reference_architecture(inventory):
    reference_architecture = inventory.get('reference-architecture')
    if not reference_architecture:
        raise UnsupportedConfig('Missing reference-architecture setting.')

    # Validate that we have at least one base architecture in the list
    if len(BASE_ARCHS.intersection(reference_architecture)) == 0:
        raise UnsupportedConfig('Missing base architecture')

    if (DBAAS in reference_architecture and
            COMPUTE not in reference_architecture):
        raise UnsupportedConfig('dbaas cannot be used without '
                                'private-compute-cloud.')

    if (SWIFT_MIN in reference_architecture and
            'swift' not in reference_architecture):
        raise UnsupportedConfig('swift-minimum-hardware cannot be used alone')

    # Validate ceph standalone is alone
    if CEPH in reference_architecture and len(reference_architecture) != 1:
        raise UnsupportedConfig('The ceph-standalone reference architecture '
                                'cannot be used in conjunction with other '
                                'reference architectures.')


def validate_swift(inventory):
    # We only support these layouts for Swift nodes and services:
    # proxy, metadata, object nodes with ring data set appropriately
    # proxy, converged object and metadata
    # if swift-minimum-hardware is specified we must have no proxy nodes,
    # no metadata nodes specified, and object servers must be converged

    reference_architecture = inventory.get('reference-architecture', [])
    if 'swift' not in reference_architecture:
        return

    converged_metadata_object = _has_converged_metadata_object(inventory)
    separate_metadata_object = _has_separate_metadata_object(inventory)
    if SWIFT_MIN in reference_architecture:
        if 'swift-proxy' in inventory.get('node-templates'):
            msg = ('The swift-proxy node template must not be used with the '
                   'swift-minimum-hardware reference architecture.')
            raise UnsupportedConfig(msg)
        if not converged_metadata_object:
            msg = ('When the swift-minimum-hardawre reference architecture is '
                   'specified, the account, container, and object rings must '
                   'be converged in the swift-object node template.')
            raise UnsupportedConfig(msg)
    else:
        if 'swift-proxy' not in inventory.get('node-templates'):
            msg = 'The swift-proxy node template was not found.'
            raise UnsupportedConfig(msg)

        if not (converged_metadata_object or separate_metadata_object):
            msg = ('The configuration of the swift-metadata, and swift-object '
                   'nodes and their corresponding account, container, and '
                   'object rings organization is not supported.')
            raise UnsupportedConfig(msg)


def _has_converged_metadata_object(inventory):
    # Return true only if:
    # object template and no metadata template
    # and container, account, and object settings are all on object template
    swift_meta = inventory['node-templates'].get('swift-metadata')
    swift_obj = inventory['node-templates'].get('swift-object')
    if swift_obj and not swift_meta:
        required_props = {'account-ring-devices',
                          'container-ring-devices',
                          'object-ring-devices'}
        domain_settings = swift_obj.get('domain-settings', {})
        if required_props.issubset(domain_settings.keys()):
            return True

    return False


def _has_separate_metadata_object(inventory):
    # Return true only if:
    # both object and metadata templates
    # metadata has account and container ring config and no object config
    # object has object but not account and container
    swift_meta = inventory['node-templates'].get('swift-metadata')
    swift_obj = inventory['node-templates'].get('swift-object')
    if swift_obj and swift_meta:
        required_meta_props = {'account-ring-devices',
                               'container-ring-devices'}
        meta_settings = swift_meta.get('domain-settings', {})
        obj_settings = swift_obj.get('domain-settings', {})
        if (required_meta_props.issubset(meta_settings.keys()) and
                'object-ring-devices' in obj_settings.keys()):
            return True
    return False


def validate_ceph(inventory):
    # TODO this method will be filled out when the ceph standalone
    # reference architecture toolkit changes are implemented
    # Validate ceph
    # no ceph-mon when private cloud
    # ceph-mon when private cloud
    # existence of proper networks for private-cloud and ceph
    pass


def validate_ops_mgr(inventory):
    # Require that every node-template be connected to the openstack-mgmt
    # network
    required_net = 'openstack-mgmt'
    if required_net not in inventory['networks']:
        msg = ('The required openstack-mgmt network %s is '
               'missing.' % required_net)
        raise UnsupportedConfig(msg)

    # validate that the controllers and ceph-osd node templates
    # have the network
    for template_name, template in inventory.get('node-templates').iteritems():
        nets = template['networks']
        if required_net not in nets:
            msg = 'The node template %(template)s is missing network %(net)s'
            raise UnsupportedConfig(msg % {'template': template_name,
                                           'net': required_net})


def _load_yml(name):
    with open(name, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as ex:
            print(ex)
            sys.exit(1)


def main():

    parser = argparse.ArgumentParser(
        description=('Validate the config or inventory yaml file for '
                     'reference architectures.'),
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--file',
                        dest='file',
                        required=True,
                        help='The path to the config or inventory file.')

    # Handle error cases before attempting to parse
    # a command off the command line
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    validate(args.file)

if __name__ == "__main__":
    main()
