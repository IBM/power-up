.. highlight:: none

Introduction
============

OpenPOWER Cluster Genesis (OPCG) enables greatly simplified configuration of clusters of
baremetal OpenPOWER servers running Linux. It leverages widely used open
source tools such as Cobbler, Ansible and Python. Because it relies
solely on industry standard protocols such as IPMI and PXE boot, hybrid
clusters of OpenPOWER and x86 nodes can readily be supported. Currently
OPCG supports Ethernet networking with separate data and management
networks. OPCG can configure simple flat networks for typical HPC
environments or more advanced networks with VLANS and bridges for
OpenStack environments. OPCG also configures the switches in the
cluster. Currently Mellanox SX1410 is supported for the data network and
the Lenovo G8052 is supported for the management network.

Overview
--------

OPCG is designed to be easy to use. If you are implementing one of the
supported architectures with supported hardware, OPCG eliminates the
need for custom scripts or programming. It does this via a configuration
file (config.yml) which drives the cluster configuration. The
configuration file is a yaml text file which the user edits. Example
YAML files are included. The configuration process is driven from a
"deployer" node which does not need to remain in the cluster when
finished. The process is as follows;

#. Rack and cable the hardware.
#. Initialize hardware.

   - initialize switches with static ip address, userid and password.
   - insure that all cluster compute nodes are set to obtain a DHCP
     address on their BMC ports.

#. Install the OpenPOWER Cluster Genesis software on the deployer node.
#. Edit an existing config.yml file.
#. Run the OPCG software
#. Power on the cluster compute nodes.

When finished, OPCG generates a YAML formatted inventory file which can
be read by operational management software and used to seed
configuration files needed for installing a solution software stack.

Hardware and Architecture Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The OpenPOWER Cluster Genesis software supports clusters of servers
interconnected with Ethernet. The
servers must support IPMI and PXE boot. Currently single racks with single
or redundant data switches (with MLAG) are supported. Multiple racks can
be interconnected with traditional two tier access-aggregation
networking.  In the future we plan to support two tier leaf-spine networks
with L3 interconnect capable of supporting VXLAN.

Networking
~~~~~~~~~~

The data network is implemented using the Mellanox SX1410 10 Gb switch.
Currently OPCG supports up to four ethernet interfaces. These interfaces
can be bonded in pairs with support for LAG or MLAG.

Templates are used to define multiple network configurations in the config.yml file.
These can be physical ports, bonded ports, Linux bridges or vLANS. Physical ports can be
renamed to ease installation of additional software stack elements.

Data switches can be set to "passive" mode to allow deployment without
supplying login credentials to the switch management interfaces. This mode
requires the user to manually write switch MAC address tables to file and to
configure the data switch in accordance with the defined networks. The client
networks will still be configured by Cluster Genesis.

Compute Nodes
~~~~~~~~~~~~~

OPCG supports clusters of heterogeneous compute nodes. Users can define any number of
node types by creating templates in a config file. Node templates can
include any network templates defined in the network templates section.  The combination of
node templates and network templates allows great flexibility in building heterogeneous clusterx with nodes
dedicated to specific purposes.

Supported Hardware
~~~~~~~~~~~~~~~~~~~

OpenPOWER Compute Nodes;

-  S812LC
-  S822LC
-  Tyan servers derived from the above 2 nodes are generally supported.
-  SuperMicro OpenPOWER servers

x86 Compute Nodes;

-  Lenovo x3550
-  Lenovo x3650

Data Switches;

-  Mellanox SX1410
-  Mellanox SX1710

Support for Lenovo G8264 is planned

Management Switches;

-  Lenovo G8052

Prerequisite hardware setup
============================

Hardware initialization
-----------------------

-  Insure the cluster is cabled according to build instructions and that
   a list of all switch port to compute node connections is available
   and verified. Note that every node to be deployed, must have a BMC
   and PXE connection to a management switch. (see the example cluster
   in Appendix-D)
-  Cable the deployer node to the cluster management network. It is
   strongly recommended that the deployer node be connected directly to
   the management switch. For large cluster deployments, a 10 Gb
   connection is recommended. The deployer node must also have access to
   the public internet (or site) network for accessing software and operating
   system image files.  If the cluster management network does not have
   external access, an alternate connection with external access must be
   provided such as the cluster data network, or wireless etc.
-  Insure that the BMC ports of all cluster nodes are configured to
   obtain an IP address via DHCP.
-  If this is a first time OS install, insure that all PXE ports are
   also configured to obtain an ip address via DHCP.  On OpenPOWER
   servers, this is typically done using the Petitboot menus.
-  Acquire any needed public and or site network addresses
-  Insure you have a config.yml file to drive the cluster configuration.
   If necessary, edit / create the config.yml file (see section
   `4 <#anchor-4>`__ `Creating the config.yml File <#anchor-4>`__)
-  Configure data switch(es) For out of box installation, it is usually
   easiest to configure the switch using a serial connection. See the
   switch installation guide. Using the Mellanox configuration wizard;

   -  assign hostname
   -  set DHCP to no for management interfaces
   -  set zeroconf on mgmt0 interface: to no
   -  do not enable ipv6 on management interfaces
   -  assign static ip address. This must match the address specified in
      the config.yml file (keyname: ipaddr-data-switch:) and be in
      a *different* subnet than your cluster management subnet used for BMC
      and PXE communication.\*
   -  assign netmask. This must match the netmask of the subnet the
      deployer will use to access the management port of the switch.
   -  default gateway
   -  Primary DNS server
   -  Domain name
   -  Set Enable ipv6 to no
   -  admin password. This must match the password specified in the
      config.yml file (keyword: password-data-switch:). Note that all
      data switches in the cluster must have the same userid and
      password.
   -  disable spanning tree (typical industry standard commands;
      *enable, configure terminal, no spanning-tree* or for Lenovo
      switches *spanning-tree mode disable*)
   -  enable SSH login. *(ssh server enable)*
   -  If this switch has been used previously, delete any existing vlans
      which match those specified in the network template section of the
      config.yml file. This insures that only those nodes specified in
      the config file have access to the cluster. (for a brand new
      switch this step can be ignored)

      -  login to the switch::

          enable
          configure terminal
          show vlan

         note those vlans that include the ports of the nodes to be included in the new cluster and remove those vlans or remove those ports from existing vlans::

          no vlan n

   -  Save config.  In switch config mode::

          configuration write

      Note that the ip addresses of the management interface used by Cluster Genesis
      for the data and management switches in your cluster must all be in the same subnet.
      The address on the management switch is assigned and configured by Cluster Genesis
      from information you provide in the config.yml file. An initial management ip address
      must be present on the management switch and specified in the config.yml file under
      the ipaddr-mgmt-switch-external keyname.
      This initial address is left in place and available for external management and
      monitoring of the switch.  The management address to be used by cluster genesis must
      be configured by the user ahead of time and be accessible from the deployer node.

   -  If using redundant data switches with MLAG, configure link aggregation
      (LAG) on the interswitch peer links (IPL) links.  (It is important to
      do this before cabling multiple links between the switches which will
      otherwise result in loops)::

        switch> en
        switch# conf t
        switch(config)# interface port-channel 6    (example port channel No.  We advise to use the number of the lowest port in the group
        switch(config interface port-channel 1) # exit
        switch(config)# lacp
        switch(config)# interface ethernet 1/6-1/7      (example port channel #s eg ports 6 and 7)
        switch(config interface ethernet 1/6-1/7)# channel-group 6 mode active
        switch(config interface ethernet 1/6-1/7)# exit

-  Configure Management switch(es) (for out of box installation, it is
   usually necessary to configure the switch using a serial connection.
   See the switch installation guide. For additional info on Lenovo G8052 specific
   commands, see Appendix G. and the *Lenovo RackSwitch G8052 Installation guide*)

   -  Enable IP interface mode for the management interface::

        RS G8052(config)# interface ip 1

   -  assign a static ip address, netmask and gateway address to the management interface.
      This must match the address specified in
      the config.yml file (keyname: ipaddr-mgmt-switch-external:) and be in a
      *different* subnet than your cluster management subnet::

        RS G8052(config-ip-if)# ip address 192.168.32.20 (example IP address)
        RS G8052(config-ip-if)# ip netmask 255.255.255.0
        RS G8052(config-ip-if)# vlan 1       (User selectable, ussually default vlan 1 is used)
        RS G8052(config-ip-if)# enable
        RS G8052(config-ip-if)# exit

   -  Optionally configure a default gateway and enable the gateway::

        RS G8052(config)# ip gateway 1 address 192.168.32.1  (example ip address)
        RS G8052(config)# ip gateway 1 enable

   -  admin password. This must match the password specified in the
      config.yml file (keyword: password-mgmt-switch:). Note that all
      management switches in the cluster must have the same userid and
      password.  The following command is interactive::

        access user administrator-password

   -  disable spanning tree (for Lenovo switches *enable, configure
      terminal, spanning-tree mode disable*)::

        spanning-tree mode disable

   -  enable secure https and SSH login::

        ssh enable
        ssh generate-host-key
        access https enable


   -  Save the config (For Lenovo switches, enter config mode
      For additional information, consult vendor documentation)::

        copy running-config startup-config

Setting up the Deployer Node
----------------------------

Requirements; It is recommended that the deployer node have at least one
available core of a XEON class processor, 16 GB of memory free and 64 GB
available disk space. For larger cluster deployments, additional cores,
memory and disk space are recommended. A 4 core XEON class processor
with 32 GB memory and 320 GB disk space is generally adequate for
installations up to several racks.

The deployer node requires internet access.  The interface associated with
the default route is used by the deployer for configuring the cluster.  This requires that
the default route be through the management switch.  This restriction will be removed in above
future release of Cluster gensesis.

**Set up the Deployer Node** (to be automated in the future)

-  Deployer OS Requirements:
    - Ubuntu
        - Release 14.04LTS or 16.04LTS
        - SSH login enabled
        - sudo priviledges
    - RHEL
        - Release 7.x
        - Extra Packages for Enterprise Linux (EPEL) repository enabled
          (https://fedoraproject.org/wiki/EPEL)
        - SSH login enabled
        - sudo priviledges
-  Optionally, assign a static, public ip address to the BMC port to
   allow external control of the deployer node.
-  login into the deployer and install the vim, vlan and bridge-utils packages
    - Ubuntu::

        $ sudo apt-get update
        $ sudo apt-get install vim vlan bridge-utils

    - RHEL::

        $ sudo yum install vim vlan bridge-utils

**Note**: Genesis uses the port associated with the default route to access the management
switch (ie eth0).  This must be defined in /etc/network/interfaces (Ubuntu) or the ifcfg-eth0
file (RedHat).

ie::

  auto eth0
  iface eth0 inet manual
