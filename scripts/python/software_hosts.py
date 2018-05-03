#!/usr/bin/env python
# Copyright 2018 IBM Corp.
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

import click
import os.path

from inventory import generate_dynamic_inventory
import lib.logger as logger
from lib.genesis import get_dynamic_inventory_path
from lib.genesis import get_playbooks_path


def _expand_children(dynamic_inventory, children_list):
    """Replace each children item with expanded dictionary
    Args:
        dynamic_inventory (dict): Dynamic inventory dictionary
        children_list (list): List of children

    Returns:
        dict: Children dictionaries from dynamic inventory
    """
    children_dict = {}
    for child in children_list:
        children_dict[child] = dynamic_inventory[child]
        if 'children' in children_dict[child]:
            children_dict[child]['children'] = _expand_children(
                dynamic_inventory,
                children_dict[child]['children'])
    return children_dict


def _get_inventory_summary(dynamic_inventory, top_level_group='all'):
    """Get the Ansible inventory structured as a nested dictionary
    with a single top level group (default 'all').

    Args:
        dynamic_inventory (dict): Dynamic inventory dictionary
        top_level_group (str): Name of top level group

    Returns:
        dict: Inventory dictionary, including groups, 'hosts',
              'children', and 'vars'.
    """
    inventory_summary = {top_level_group: dynamic_inventory[top_level_group]}
    if 'children' in inventory_summary[top_level_group]:
        inventory_summary[top_level_group]['children'] = _expand_children(
            dynamic_inventory,
            inventory_summary[top_level_group]['children'])
    return inventory_summary


def _get_hosts_list(dynamic_inventory, top_level_group='all'):
    """Get a list of hosts.

    Args:
        dynamic_inventory (dict): Dynamic inventory dictionary
        top_level_group (str): Name of top level group

    Returns:
        list: List containing all inventory hosts
    """
    hosts_list = []
    if 'hosts' in dynamic_inventory[top_level_group]:
        hosts_list += dynamic_inventory[top_level_group]['hosts']
    if 'children' in dynamic_inventory[top_level_group]:
        for child in dynamic_inventory[top_level_group]['children']:
            hosts_list += _get_hosts_list(dynamic_inventory, child)
    return hosts_list


def _get_groups_hosts_dict(dynamic_inventory, top_level_group='all'):
    """Get a dictionary of groups and hosts. Hosts will be listed under
    their lowest level group membership only.

    Args:
        dynamic_inventory (dict): Dynamic inventory dictionary
        top_level_group (str): Name of top level group

    Returns:
        dict: Dictionary containing groups with lists of hosts
    """
    groups_hosts_dict = {}
    if 'hosts' in dynamic_inventory[top_level_group]:
        if top_level_group not in groups_hosts_dict:
            groups_hosts_dict[top_level_group] = []
        groups_hosts_dict[top_level_group] += (
            dynamic_inventory[top_level_group]['hosts'])
    if 'children' in dynamic_inventory[top_level_group]:
        for child in dynamic_inventory[top_level_group]['children']:
            groups_hosts_dict.update(_get_groups_hosts_dict(dynamic_inventory,
                                                            child))
    return groups_hosts_dict


def _get_groups_hosts_string(dynamic_inventory):
    """Get a string containing groups and hosts formatted in the
    Ansible inventory 'ini' style. Hosts will be listed under their
    lowest level group membership only.

    Args:
        dynamic_inventory (dict): Dynamic inventory dictionary

    Returns:
        str: String containing groups with lists of hosts
    """
    output_string = ""
    groups_hosts_dict = _get_groups_hosts_dict(dynamic_inventory)
    for host in groups_hosts_dict['all']:
        output_string += host + "\n"
    output_string += "\n"
    for group, hosts in groups_hosts_dict.items():
        if group != 'all':
            output_string += "[" + group + "]\n"
            for host in hosts:
                output_string += host + "\n"
            output_string += "\n"
    return output_string.rstrip()


def get_ansible_inventory():
    log = logger.getlogger()
    inventory_choice = None
    dynamic_inventory_path = get_dynamic_inventory_path()
    software_hosts_file_path = (
        os.path.join(get_playbooks_path(), 'software_hosts'))

    dynamic_inventory = generate_dynamic_inventory()

    if len(set(_get_hosts_list(dynamic_inventory)) -
           set(['deployer', 'localhost'])) > 0:
        print("Ansible Dynamic Inventory found:")
        print("--------------------------------")
        print(_get_groups_hosts_string(dynamic_inventory))
        print("--------------------------------")
        if click.confirm('Do you want to use this inventory?'):
            print("Using Ansible Dynamic Inventory")
            inventory_choice = dynamic_inventory_path
        else:
            print("NOT using Ansible Dynamic Inventory")

    if inventory_choice is None and os.path.isfile(software_hosts_file_path):
        while True:
            print("Software inventory file found at '{}':"
                  .format(software_hosts_file_path))
            print("--------------------------------------------------")
            with open(software_hosts_file_path, 'r') as hosts_file:
                print(hosts_file.read())
            print("--------------------------------------------------")
            if click.confirm('Do you want to use this inventory as-is?'):
                print("Using '{}' as inventory"
                      .format(software_hosts_file_path))
                inventory_choice = software_hosts_file_path
                break
            elif click.confirm('Do you want to edit this inventory?'):
                click.edit(filename=software_hosts_file_path)
            else:
                print("NOT using Ansible 'hosts' file")
                break

    if (inventory_choice is None and
            click.confirm('Do you want to create a new software inventory?')):
        hosts_template = ("""\
# Ansible Inventory File
#
# For detailed information visit:
#   http://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html
#
# Group names are defined within brackets
# Hosts can given with an FQDN or IP address
#   e.g.:
#   [group1]
#   host1.domain.com  # host1
#   192.168.1.21      # host2
#
localhost ansible_connection=local

[group1]
          # define first host on this line _before the "#"
""")
        hosts = None
        while hosts is None:
            hosts = click.edit(hosts_template)
            if hosts is not None:
                with open(software_hosts_file_path, "w") as new_hosts_file:
                    new_hosts_file.write(hosts)
                inventory_choice = software_hosts_file_path
            elif not click.confirm('File not written! Try again?'):
                break

    log.debug("User software inventory choice: {}".format(inventory_choice))
    return inventory_choice


if __name__ == '__main__':
    logger.create()

    print(get_ansible_inventory())
