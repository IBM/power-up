
Appendix - D Example system 1 Simple Flat Cluster
=================================================

.. figure:: https://raw.githubusercontent.com/wiki/open-power-ref-design/cluster-genesis/images/cluster-genesis-simple_flat_cluster.png
   :alt: 
   :width: 3.38350in
   :height: 4.23070in

A Sample config.yml file;

The config file below defines two compute node templates and two network
templates

ipaddr-mgmt-network: 192.168.16.0/20

ipaddr-mgmt-switch:

 rack1: 192.168.16.5

ipaddr-data-switch:

 rack1: 192.168.16.25

redundant-network: false

userid-default: ubuntu

password-default: passw0rd

userid-mgmt-switch: admin

password-mgmt-switch: admin

userid-data-switch: admin

password-data-switch: admin

networks:

 physnet1:

 description: Organization site or external network

 addr: 10.40.204.0/24

 broadcast: 10.40.204.255

 gateway: 10.40.204.1

 dns-nameservers: 9.3.1.200

 dns-search: aus.stglabs.ibm.com

 method: static

 eth-port: eth10

 physnet2:

 description: Interface for eth11

 method: manual

 eth-port: eth11

 ctrl:

 description: Control Network

 bridge: br-ctrl

 method: static

 tcp\_segmentation\_offload: off

 addr: 172.29.236.0/22

 vlan: 210

 eth-port: eth10

 data:

 description: Data Network

 bridge: br-data

 method: static

 addr: 172.29.240.0/22

 vlan: 30 # data vlan id

 eth-port: eth11

node-templates:

 node-type1:

 hostname: management

 userid-ipmi: ADMIN

 password-ipmi: ADMIN

 cobbler-profile: ubuntu-14.04.4-server-amd64

 name-interfaces:

 mac-pxe: eth15

 mac-eth10: eth10

 mac-eth11: eth11

 ports:

 pxe:

 rack1: [2]

 ipmi:

 rack1: [1]

 eth10:

 rack1: [5]

 networks:

 - physnet1

 - ctrl

node-type2:

 hostname: compute

 userid-ipmi: ADMIN

 password-ipmi: admin

 cobbler-profile: ubuntu-14.04.4-server-ppc64el

 name-interfaces:

 mac-pxe: eth15

 mac-eth10: eth10

 mac-eth11: eth11

 ports:

 pxe:

 rack1: [4, 6]

 ipmi:

 rack1: [3, 5]

 eth10:

 rack1: [6, 8]

 eth11:

 rack1: [7, 9]

 networks:

 - physnet1

 - physnet2

 - ctrl

 - data
