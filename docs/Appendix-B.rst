
Appendix - B The System Configuration File 
===========================================

Genesis of the OpenPOWER Cloud Reference Config is controlled by the
opcr.cfg.yml file. This file is stored in YAML format. The definition of
the fields and the YAML file format are documented below.

config.yml Field Definitions (incomplete)
-------------------------------------------

+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| **Keyword**               | **Description**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | **Format**     | **Example**       |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| ipaddr-mgmt-network       | Management network address in CIDR format This is the network that the PXE and IPMI ports are on. The IPMI ports and the Mgmt/PXE ports of all nodes in the system must be accessible on this subnet. The management ports of all management switches and data switches must be on a different subnet.                                                                                                                                                                                                                                                                                                                                                                | a.b.c.d/n      | 192.168.16.0/20   |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| redundant-network         | Indicates the configuration of the data network. The data network can be redundant, in which case there are redundant top of rack (leaf) switches and bonded node ports, or non-redundant, in which case there is a single top of rack switch. 0,1 indicates non-redundant, redundant                                                                                                                                                                                                                                                                                                                                                                                 | n              | 0                 |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| userid-default            | Default userid to be set for all cluster node host OS access                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                |                   |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| password-default          | Default password to be set for all cluster node OS access                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                |                   |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| ipaddr-mgmt-switch        | list of static ipv4 addresses of the management interface of the management switches in each rack or cell. The ip addresses of the management interfaces of all management switches must be manually configured on the management switch before genesis begins. The OpenPOWER cluster genesis will look for management switches at the specified address. Usually, one management switch would be physically located in each rack or with each cell. All of the management interfaces for the management switch and the data switches must reside in one subnet. This subnet must be different than the subnet used for the cluster management network.               | a.b.c.d        | 192.168.80.32     |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| userid-mgmt-switch        | Userid of the management switch's management port. User ID's of the management ports of all management switches must be manually configured on the management switch before genesis begins. During genesis, all management switches are assumed to have the same userid and password. If not specified, the default userid will be used.                                                                                                                                                                                                                                                                                                                              |                |                   |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| password-mgmt-switch      | Pasword of the management switch's management port. Passwords of the mangement ports of all management switches must be manually configured on the management switch before genesis begins. During genesis, all management switches are assumed to have the same userid and password.                                                                                                                                                                                                                                                                                                                                                                                 |                |                   |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| ipaddr-mgmt-aggr-switch   | ipv4 address of the aggregation management switch. The management network is expected to be in a typical access-aggregation layout with an access switch in each rack, all connected to an aggregation switch.                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                |                   |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| ipaddr-data-switch        | This is a list of ipv4 addresses of the management port of the data switches. This address must be manually configured on the data switches before genesis begins. If the data network is redundant, a 2\ :sup:`nd` data switch is looked for at the next sequential address. Users should also plan to allocate one or more additional ip addresses for each pair of data switches. These addresses are used by the switches for inter-switch communication. All of the management interfaces for the management switches and the data switches must reside in one subnet. This subnet must be different than the subnet used for the cluster management network.    | a.b.c.d        | 192.168.80.36     |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| userid-data-switch        | User ID of the management port of the data switch. This userid must be manually configured on the data switch(es) prior to genesis.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | userid         | joeuser           |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+
| password-data-switch      | Password for the management port of the data switch. This password must be manually configured on the data switch(es) prior to genesis.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | password       | passw0rd          |
+---------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------+-------------------+


config.yml YAML File format:
----------------------------

::

    ---
    # Copyright 2016 IBM Corp.
    #
    # All Rights Reserved.
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    # http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    # This sample configuration file documents all of the supported key values
    # supported by the genesis software. It can be used as the basis for creating
    # your own config.yml file. Note that keywords with a leading underscore
    # can be changed by the end user as appropriate for your application.(e.g.
    # "_rack1" could be changed to "base-rack")

    # This sample configuration file documents all of the supported key values
    # supported by the genesis software.  It can be used as the basis for creating
    # your own config.yml file.  Note that keywords with a leading underscore
    # can be changed by the end user as appropriate for your application. (e.g.
    # "_rack1" could be changed to "base-rack")

    version: 1.1

    ipaddr-mgmt-network: 192.168.16.0/20
    ipaddr-mgmt-client-network: 192.168.20.0/24
    vlan-mgmt-network: 16
    vlan-mgmt-client-network: 20
    port-mgmt-network: 1
    # NOTE: The "_rack:" keywords must match the the corresponding rack keyword
    # under the keyword;
    # node-templates:
    #     _node name:
    #         ports:
    port-mgmt-data-network:
        _rack1: 47
    ipaddr-mgmt-switch:
        _rack1: 192.168.16.20
    ipaddr-data-switch:
        _rack1: 192.168.16.25
    redundant-network: false
    userid-default: user
    password-default: passw0rd
    # An encrypted password hash can also be provided using the following format:
    # password-default-crypted: $6$STFB8U/AyA$sVhg5a/2RvDiXof9EhADVcUm/7Tq8T4m0dcdHLFZkOr.pCjJr2eH8RS56W7ZUWw6Zsm2sKrkcS4Xc8910JMOw.
    userid-mgmt-switch: user        # applied to all mgmt switches
    password-mgmt-switch: passw0rd  # applied to all mgmt switches
    userid-data-switch: user
    password-data-switch: passw0rd
    # Rack information is optional (not required to be present)
    racks:
        - rack-id: rack1
          data-center: dataeast
          room: room33
          row: row1
    networks:
        _external1:
            description: Organization site or external network
            addr: 9.3.89.0/24
            available-ips:
                - 9.3.89.14            # single address
                - 9.3.89.18 9.3.89.22  # address range
                - 9.3.89.111 9.3.89.112
                - 9.3.89.120
            broadcast: 9.3.89.255
            gateway: 9.3.89.1
            dns-nameservers: 9.3.1.200
            dns-search: your.dns.com
            method: static
            eth-port: eth10
            mtu: 9000
        _external2:
            description: Interface for eth11
            method: manual
            eth-port: eth11
        _pxe-dhcp:
            description: Change pxe port(eth15) to dhcp
            method: dhcp
            eth-port: eth15
        _standalone-bond0:
            description: Multilink bond
            bond: mybond0
            addr: 10.0.16.0/22
            available-ips:
                - 10.0.16.150              # single address
                - 10.0.16.175 10.0.16.215  # address range
            broadcast: 10.0.16.255
            gateway: 10.0.16.1
            dns-nameservers: 10.0.16.200
            dns-search: mycompany.domain.com
            method: static
            # name of physical interfaces to bond together.
            bond-interfaces:
                - eth0
                - eth1
            # if necessary not all bond modes support a primary slave
            bond-primary: eth10
            # bond-mode, needs to be one of 7 types
            # either name or number can be used.
            # 0 balance-rr
            # 1 active-backup
            # 2 balance-xor
            # 3 broadcast
            # 4 802.3ad
            # 5 balance-tlb
            # 6 balance-alb
            # bond-mode: active-backup
            bond-mode: 1
            # there is a long list of optional bond arguments.
            # Specify them here and they will be added to end of bond definition
            optional-bond-arguments:
                bond-miimon: 100
                bond-lacp-rate: 1
        _manual-bond1:
            description: bond network to be used by future bridges
            bond: bond1
            method: manual
            bond-mode: balance-rr
            bond-interfaces:
                - eth10
                - eth11
        _cluster-mgmt:
            description: Cluster Management Network
            bridge: br-mgmt
            method: static
            tcp_segmentation_offload: "off"  # on/off values need to be enclosed in quotes
            addr: 172.29.236.0/22
            vlan: 10
            eth-port: eth10
            bridge-port: veth-infra  # add a veth pair to the bridge
        _vm-vxlan-network:
            description: vm vxlan Network
            bridge: br-vxlan
            method: static
            addr: 172.29.240.0/22
            vlan: 30
            eth-port: eth11
        _vm-vlan-network:
            description: vm vlan Network
            bridge: br-vlan
            method: static
            addr: 0.0.0.0/1  # Host nodes do not get IPs assigned in this network
            eth-port: eth11  # No specified vlan.  Allows use with untagged vlan
            bridge-port: veth12
    node-templates:
        _node-name:
            hostname: controller
            userid-ipmi: userid
            password-ipmi: password
            cobbler-profile: ubuntu-14.04.4-server-amd64
            os-disk: /dev/sda
            users:
                - name: user1
                  groups: sudo
                - name: testuser1
                  groups: testgroup
            groups:
                - name: testgroup
            name-interfaces:
                mac-pxe: eth15    # This keyword is paired to ports: pxe: keyword
                mac-eth10: eth10  # This keyword is paired to ports: eth10: keyword
                mac-eth11: eth11  # This keyword is paired to ports: eth11: keyword
            # Each host has one network interface for each of these ports and
            # these port numbers represent the switch port number to which the host
            # interface is physically cabled.
            # To add or remove hosts for this node-template you add or remove
            # switch port numbers to these ports.
            ports:
                pxe:
                    _rack1:
                        - 1
                        - 2
                        - 3
                ipmi:
                    _rack1:
                        - 4
                        - 5
                        - 6
                eth10:
                    _rack1:
                        - 1
                        - 2
                        - 3
                eth11:
                    _rack1:
                        - 4
                        - 5
                        - 6
            networks:
                - _cluster-mgmt
                - _vm-vxlan-network
                - _vm-vlan-network
                - _external1
                - _external2
                - _pxe-dhcp
                - _manual-bond1
                - _standalone-bond0
        _compute:
            hostname: compute
            userid-ipmi: userid
            password-ipmi: password
            cobbler-profile: ubuntu-14.04.4-server-amd64
            name-interfaces:
                mac-pxe: eth15
                mac-eth10: eth10
                mac-eth11: eth11
            # Each host has one network interface for each of these ports and
            # these port numbers represent the switch port number to which the host
            # interface is cabled.
            # To add or remove hosts for this node-template you add or remove
            # switch port numbers to these ports.
            ports:
                pxe:
                    _rack1:
                        - 7
                        - 8
                        - 9
                ipmi:
                    _rack1:
                        - 10
                        - 11
                        - 12
                eth10:
                    _rack1:
                        - 7
                        - 8
                        - 9
                eth11:
                    _rack1:
                        - 10
                        - 11
                        - 12
            networks:
                - _cluster-mgmt
                - _vm-vxlan-network
                - _vm-vlan-network
                - _external1
                - _external2
                - _pxe-dhcp
                - _manual-bond1
                - _standalone-bond0

    software-bootstrap:
        all: apt-get update
        compute[0]: |
            apt-get update
            apt-get upgrade -y
    # Additional key/value pairs are not processed by Genesis, but are copied into
    # the inventory.yml file and made available to post-Genesis scripts and/or
    # playbooks.
