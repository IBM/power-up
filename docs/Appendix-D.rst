
Appendix - D Example system 1 Simple Flat Cluster
=================================================

.. figure:: _images/simple_flat_cluster.png
     :height: 350
     :align: center

     A simple flat cluster with two node types

A Sample config.yml file;

The config file below defines two compute node templates and multiple network
templates.  The sample cluster can be configured with the provided config.yml file.
The deployer node needs to have access to the internet for accessing packages.
Internet access must then be provided via one of the dotted line paths shown
in the figure above or alternately via a wireless or dedicated interface.

Various OpenPOWER nodes can be used such as the S821LC.  The deployer node can be OpenPOWER
or alternately a laptop which does not need to remain in the cluster.  The data switch can be
Mellanox SX1700 or SX1410. The management switch must be a
Lenovo G8052 switch::

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
    port-mgmt-network: 46
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
    userid-mgmt-switch: user        # applies to all mgmt switches
    password-mgmt-switch: passw0rd  # applies to all mgmt switches
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
            addr: 10.3.89.0/24
            available-ips:
                - 10.3.89.14            # single address
                - 10.3.89.18 10.3.89.22  # address range
                - 10.3.89.111 10.3.89.112
                - 10.3.89.120
            broadcast: 10.3.89.255
            gateway: 10.3.89.1
            dns-nameservers: 8.8.8.8
            dns-search: your.dns.com
            method: static
            eth-port: eth10
            mtu: 9000
        _external2:
            description: Interface for eth11
            method: manual
            eth-port: eth11
            mtu: 9000
        _pxe-dhcp:
            description: Change pxe port(eth15) to dhcp
            method: dhcp
            eth-port: eth15
        _cluster-bridge:
            description: Cluster Management Network
            bridge: br-clst
            method: static
            tcp_segmentation_offload: "off"  # on/off values need to be enclosed in quotes
            addr: 172.29.236.0/22
            vlan: 10
            eth-port: eth10
            bridge-port: veth-infra  # add a veth pair to the bridge
    node-templates:
        _node-type1:
            hostname: charlie
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
                        - 2
                ipmi:
                    _rack1:
                        - 1
                eth10:
                    _rack1:
                        - 5
            networks:
                - _cluster-mgmt
                - _external1
                - _external2
                - _pxe-dhcp
        _node-type2:
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
                        - 4
                        - 6
                ipmi:
                    _rack1:
                        - 3
                        - 5
                eth10:
                    _rack1:
                        - 6
                        - 8
                eth11:
                    _rack1:
                        - 7
                        - 9
            networks:
                - _cluster-mgmt
                - _external1
                - _external2
                - _pxe-dhcp

    software-bootstrap:
        all: apt-get update
    #   _node-type2[0]: |
    #       export GIT_BRANCH=master
    #       URL="https://raw.githubusercontent.com/open-power-ref-design/openstack-recipes/${GIT_BRANCH}/scripts/bootstrap-solution.sh"
    #       wget ${URL}
    #       chmod +x bootstrap-solution.sh
    #       ./bootstrap-solution.sh

# Additional key/value pairs are not processed by Genesis, but are copied into
# the inventory.yml file and made available to post-Genesis scripts and/or
# playbooks.
