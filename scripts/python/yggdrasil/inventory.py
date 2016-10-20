#!/usr/bin/env python
# Copyright 2016 IBM Corp.
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

""" This is an ansible dynamic inventory module which loads an inventory file
describing networks, nodes, and their relationships and outputs ansible
inventory containing the host groups, hosts and network information
required to allow the configuration of the network interfaces on the nodes.

An example output of this generation is:
{
    "controllers": [
        "192.168.0.111",
        "192.168.0.112",
        "192.168.0.113"
    ],
    "ceph-osd": [
        "192.168.0.121",
        "192.168.0.122",
        "192.168.0.123",
        "192.168.0.124"
    ],
    "all": {
        "children": [
            "controllers",
            "ceph-osd",
            "compute"
        ],
        "vars": {
            "networks": {
                "openstack-stg": {
                    "bridge": "br-storage",
                    "network": "172.29.244.0",
                    "eth-port": "eth10",
                    "vlan": 20,
                    "tcp_segmentation_offload": false,
                    "netmask": "255.255.252.0",
                    "method": "static",
                    "description": "OpenStack storage network"
                },
                "openstack-tenant-vlan": {
                    "bridge": "br-vlan",
                    "description": "Openstack Networking vlan",
                    "method": "static",
                    "eth-port": "eth11"
                },
                "external2": {
                    "description": "Interface for eth11",
                    "method": "manual",
                    "eth-port": "eth11"
                },
                "external1": {
                    "network": "10.40.204.0",
                    "eth-port": "eth10",
                    "dns-search": "acme.com",
                    "dns-nameservers": "10.40.1.200",
                    "method": "static",
                    "broadcast": "10.40.204.255",
                    "netmask": "255.255.255.0",
                    "gateway": "10.40.204.1",
                    "description": "Site network"
                },
                "ceph-replication": {
                    "bridge": "br-replication",
                    "network": "172.29.248.0",
                    "eth-port": "eth11",
                    "vlan": 40,
                    "netmask": "255.255.252.0",
                    "method": "static",
                    "description": "OpenStack storage network"
                },
                "openstack-tenant-vxlan": {
                    "bridge": "br-vxlan",
                    "network": "172.29.240.0",
                    "eth-port": "eth11",
                    "vlan": 30,
                    "netmask": "255.255.252.0",
                    "method": "static",
                    "description": "Openstack Networking VXLAN"
                },
                "openstack-mgmt": {
                    "bridge": "br-mgmt",
                    "network": "172.29.236.0",
                    "eth-port": "eth10",
                    "vlan": 10,
                    "tcp_segmentation_offload": false,
                    "netmask": "255.255.252.0",
                    "method": "static",
                    "description": "OpenStack management network"
                }
            }
        }
    },
    "compute": [
        "192.168.0.125",
        "192.168.0.126",
        "192.168.0.127"
    ],
    "_meta": {
        "hostvars": {
            "192.168.0.124": {
                "host_networks": {
                    "ceph-replication": {
                        "addr": "172.29.248.4"
                    },
                    "openstack-stg": {
                        "addr": "172.29.244.6"
                    },
                    "external1": {
                        "addr": "10.40.204.179"
                    }
                },
                "name_interfaces": {
                    "eth11": "98:be:94:5c:f0:05",
                    "eth10": "98:be:94:5c:f0:04",
                    "eth15": "98:be:94:5c:f0:06"
                }
            },
            "192.168.0.123": {
                "host_networks": {
                    "ceph-replication": {
                        "addr": "172.29.248.3"
                    },
                    "openstack-stg": {
                        "addr": "172.29.244.5"
                    },
                    "external1": {
                        "addr": "10.40.204.178"
                    }
                },
                "name_interfaces": {
                    "eth15": "98:be:94:5c:ee:b6"
                }
            },
            "192.168.0.122": {
                "host_networks": {
                    "ceph-replication": {
                        "addr": "172.29.248.2"
                    },
                    "openstack-stg": {
                        "addr": "172.29.244.4"
                    },
                    "external1": {
                        "addr": "10.40.204.177"
                    }
                },
                "name_interfaces": {
                    "eth15": "98:be:94:5c:ef:0e"
                }
            },
            "192.168.0.121": {
                "host_networks": {
                    "ceph-replication": {
                        "addr": "172.29.248.1"
                    },
                    "openstack-stg": {
                        "addr": "172.29.244.3"
                    },
                    "external1": {
                        "addr": "10.40.204.176"
                    }
                },
                "name_interfaces": {
                    "eth11": "98:be:94:5c:f0:25",
                    "eth10": "98:be:94:5c:f0:24",
                    "eth15": "98:be:94:5c:f0:26"
                }
            },
            "192.168.0.112": {
                "host_networks": {
                    "openstack-stg": {
                        "addr": "172.29.244.10"
                    },
                    "openstack-tenant-vlan": {
                        "addr": "0.0.0.0"
                    },
                    "external2": {},
                    "external1": {
                        "addr": "10.40.204.191"
                    },
                    "openstack-tenant-vxlan": {
                        "addr": "172.29.240.1"
                    },
                    "openstack-mgmt": {
                        "addr": "172.29.236.1"
                    }
                },
                "name_interfaces": {
                    "eth15": "0c:c4:7a:51:ed:90"
                }
            },
            "192.168.0.113": {
                "host_networks": {
                    "openstack-stg": {
                        "addr": "172.29.244.2"
                    },
                    "openstack-tenant-vlan": {
                        "addr": "0.0.0.0"
                    },
                    "external2": {},
                    "external1": {
                        "addr": "10.40.204.192"
                    },
                    "openstack-tenant-vxlan": {
                        "addr": "172.29.240.2"
                    },
                    "openstack-mgmt": {
                        "addr": "172.29.236.2"
                    }
                },
                "name_interfaces": {
                    "eth15": "0c:c4:7a:51:eb:16"
                }
            },
            "192.168.0.125": {
                "host_networks": {
                    "openstack-stg": {
                        "addr": "172.29.244.7"
                    },
                    "openstack-tenant-vlan": {
                        "addr": "0.0.0.0"
                    },
                    "external2": {},
                    "external1": {
                        "addr": "10.40.204.180"
                    },
                    "openstack-tenant-vxlan": {
                        "addr": "172.29.240.3"
                    },
                    "openstack-mgmt": {
                        "addr": "172.29.236.3"
                    }
                },
                "name_interfaces": {
                    "eth15": "98:be:94:58:e4:8a"
                }
            },
            "192.168.0.111": {
                "host_networks": {
                    "openstack-stg": {
                        "addr": "172.29.244.1"
                    },
                    "openstack-tenant-vlan": {
                        "addr": "0.0.0.0"
                    },
                    "external2": {},
                    "external1": {
                        "addr": "10.40.204.190"
                    },
                    "openstack-tenant-vxlan": {
                        "addr": "172.29.240.6"
                    },
                    "openstack-mgmt": {
                        "addr": "172.29.236.6"
                    }
                },
                "name_interfaces": {
                    "eth15": "0c:c4:7a:51:ed:cc"
                }
            },
            "192.168.0.127": {
                "host_networks": {
                    "openstack-stg": {
                        "addr": "172.29.244.9"
                    },
                    "openstack-tenant-vlan": {
                        "addr": "0.0.0.0"
                    },
                    "external2": {},
                    "external1": {
                        "addr": "10.40.204.182"
                    },
                    "openstack-tenant-vxlan": {
                        "addr": "172.29.240.5"
                    },
                    "openstack-mgmt": {
                        "addr": "172.29.236.5"
                    }
                },
                "name_interfaces": {
                    "eth15": "98:be:94:58:21:82"
                }
            },
            "192.168.0.126": {
                "host_networks": {
                    "openstack-stg": {
                        "addr": "172.29.244.8"
                    },
                    "openstack-tenant-vlan": {
                        "addr": "0.0.0.0"
                    },
                    "external2": {},
                    "external1": {
                        "addr": "10.40.204.181"
                    },
                    "openstack-tenant-vxlan": {
                        "addr": "172.29.240.4"
                    },
                    "openstack-mgmt": {
                        "addr": "172.29.236.4"
                    }
                },
                "name_interfaces": {
                    "eth15": "98:be:94:58:08:86"
                }
            }
        }
    }
}
"""

import argparse
import copy
import json
import netaddr
import sys
import yaml

# The key in on nodes in the source inventory file that contains
# the IP address ansible should use for the host.
HOST_IP_KEY = 'ipv4-pxe'
# The IP address value used when a node needs an interface on the network
# without an IP address assigned.
INPUT_FILE = '/var/oprc/inventory.yml'


def load_input_file():
    with open(INPUT_FILE, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as ex:
            print(ex)
            sys.exit(1)


def generic_variable_conversion(inventory, inventory_source):
    # Generically convert top level settings in the inventory to
    # all vars and node level properties as host level vars.

    # All vars:
    for key, value in inventory_source.iteritems():
        # We don't variablize the nodes tree in all vars
        if key == 'nodes':
            continue

        var_name = _sanitize_variable_name(key)
        inventory['all']['vars'][var_name] = value

    # Flatten the nodes from the inventory into a single list
    nodes = [node for sublist in inventory_source['nodes'].values() for node
             in sublist]

    hv = inventory['_meta']['hostvars']
    # host vars:
    for node in nodes:
        for key, value in node.iteritems():
            var_name = _sanitize_variable_name(key)
            hv[node[HOST_IP_KEY]][var_name] = value


def _sanitize_variable_name(name):
    return name.replace('-', '_')


def get_host_ip_to_node(inventory_source):
    # Process the inventory file and make a map of the IP address ansible
    # will use for the host communication to the node dictionary from
    # the input inventory.
    ip_to_node = {}

    # Flatten the nodes from the inventory into a single list
    nodes = [node for sublist in inventory_source['nodes'].values() for node
             in sublist]
    for node in nodes:
        if HOST_IP_KEY in node:
            ip_to_node[node[HOST_IP_KEY]] = node
    return ip_to_node


def populate_hosts_and_groups(inventory, inventory_source):
    # Create the 'all' group and children groups based on the
    # node groupings in the source inventory.
    groups = []
    for node_group, nodes in inventory_source['nodes'].iteritems():
        groups.append(node_group)
        inventory[node_group] = [node[HOST_IP_KEY] for node in nodes]
        # Add empty hostvars
        for node in inventory[node_group]:
            inventory['_meta']['hostvars'][node] = {}

    inventory['all']['children'] = groups


def populate_network_variables(inventory, inventory_source):
    # Add the networks from the inventory source into the host_vars
    networks = copy.deepcopy(inventory_source['networks'])
    for network in networks.values():
        # Add properties network address and the netmask
        addr = network.get('addr', None)
        if addr:
            ip = netaddr.IPNetwork(addr)
            if ip.prefixlen != 1:
                # We don't put networks in with prefix length == 1 because
                # the inventory file uses this to note that while the host
                # has an interface connected to this network, that interface
                # does not directly get an IP address and the address goes
                # on a bridge.
                network['network'] = str(ip.network)
                network['netmask'] = str(ip.netmask)
    inventory['all']['vars']['networks'] = networks


def populate_host_networks(inventory, inventory_source, ip_to_node):
    hostvars = inventory['_meta']['hostvars']
    for ip, node in ip_to_node.iteritems():
        for net in inventory_source['networks'].keys():
            node_ip_addr = node.get(net+'-addr')
            # If the node is connected to this network
            if node_ip_addr is not None:
                net_addr = {'addr': node_ip_addr}
                # The IP address may be the empty string if the system
                # must have the interface but does not have an IP on the
                # interface, and bridges have the IPs.
                if not net_addr['addr']:
                    net_addr = {}
                if 'host_networks' not in hostvars[ip]:
                    hostvars[ip]['host_networks'] = {}
                hostvars[ip]['host_networks'][net] = net_addr
            elif inventory_source['networks'][net]['method'] == "dhcp":
                if 'host_networks' not in hostvars[ip]:
                    hostvars[ip]['host_networks'] = {}
                hostvars[ip]['host_networks'][net] = {}


def populate_name_interfaces(inventory, inventory_source, ip_to_node):
    for ip, node in ip_to_node.iteritems():
        template = inventory_source['node-templates'][node['template']]
        if 'name-interfaces' not in template:
            continue
        if_name_to_mac = {}
        for mac_key, if_name in template['name-interfaces'].iteritems():
            if mac_key in node:
                if_mac = node[mac_key]
                if_name_to_mac[if_name] = if_mac
        if if_name_to_mac:
            hv = inventory['_meta']['hostvars']
            hv[ip]['name_interfaces'] = if_name_to_mac


def generate_dynamic_inventory():

    inventory_source = load_input_file()
    ip_to_node = get_host_ip_to_node(inventory_source)
    # initialize the empty inventory
    inventory = {'all': {'vars': {}},
                 '_meta': {'hostvars': {}}}
    populate_hosts_and_groups(inventory, inventory_source)
    generic_variable_conversion(inventory, inventory_source)
    populate_network_variables(inventory, inventory_source)
    populate_host_networks(inventory, inventory_source,
                           ip_to_node)
    populate_name_interfaces(inventory, inventory_source, ip_to_node)
    return inventory


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host', action='store')
    args = parser.parse_args()
    if args.list:
        inventory = generate_dynamic_inventory()
    else:
        # We don't use the host argument because our inventory
        # returns all host variables in _meta when called with --list.
        # For any other arguments passed, just return this empty inventory.
        inventory = {'_meta': {'hostvars': {}}}

    return json.dumps(inventory, indent=4)


if __name__ == '__main__':
    print main()
