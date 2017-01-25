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
servers must support IPMI and PXE boot. Currently single rack 
non-redundant networking (single data switch) is supported. Support for
redundant networks and multiple racks is being added. Multiple racks can
be interconnected with traditional two tier access-aggregation
networking or two tier leaf-spine networks with L3 interconnect capable
of supporting VXLAN.

Networking
~~~~~~~~~~

The data network is implemented using the Mellanox SX1410 10 Gb switch.
OPCG will support any number of data interfaces on the compute nodes. 
(Currently OPCG supports one or two ethernet interfaces.  These interfaces 
can be bonded.)  The first release of OPCG implements non-redundant data network. A 
follow on release will support redundant switches and expansion to multiple racks.

Templates can definge multiple network configurations in the config.yml file. 
These can be physical ports, bonded ports, Linux bridges or vLANS. Physical ports can be
renamed to ease installation of additional software stack elements.

Compute Nodes
~~~~~~~~~~~~~

OPCG supports clusters of heterogeneous compute nodes. Users can define any number of
node types by creating templates in a config file. Node templates can
include any network templates defined in the network templates section.

Supported Hardware 
~~~~~~~~~~~~~~~~~~~

OpenPOWER Compute Nodes;

-  S812LC
-  S822LC
-  Tyan servers derived from the above 2 nodes are generally supported.

x86 Compute Nodes;

-  Lenovo x3550
-  Lenovo x3650
-  Lenovo RD550

Data Switches;

-  Mellanox SX1410
-  Mellanox SX1710

Support for Lenovo G8264 is planned

Management Switches;

-  Lenovo G8052
-  Lenovo G7028
-  Lenovo G7052

Prerequisites;
==============

Hardware initialization
-----------------------

-  Insure the cluster is cabled according to build instructions and that
   a list of all switch port to compute node connections is available
   and verified. Note that every node to be deployed, must have a BMC
   and PXE connection to a management switch. (see the example cluster
   in Appendix-C or D)
-  Cable the deployer node to the cluster management network. It is
   strongly recommended that the deployer node be connected directly to
   the management switch. For large cluster deployments, a 10 Gb
   connection is recommended. The deployer node must also have access to
   the public (or site) network for accessing software and image files.
   If the cluster management network does not have external access, an
   alternate connection with external access must be provided such as
   the cluster data network, or wireless etc.
-  Insure that the BMC ports of all cluster nodes are configured to
   obtain an IP address via DHCP.
-  If this is a first time OS install, insure that all PXE ports are
   also configured to obtain an ip address via DHCP.
-  Acquire any needed public and or site network addresses
-  Insure you have a config.yml file to drive the cluster configuration.
   If necessary, edit / create the config.yml file (see section
   `4 <#anchor-4>`__ `Creating the config.yml File <#anchor-4>`__)
-  Configure data switch(es) (for out of box installation, it is usually
   necessary to configure the switch using a serial connection. See the
   switch installation guide. For Mellanox switches set "zeroconf on
   mgmt0 interface:" to no)

   -  assign hostname
   -  assign static ip address. This must match the address specified in
      the config.yml file (keyname: ipaddr-data-switch:) and be in
      a *different* subnet than your cluster management subnet used for BMC
      and PXE communication.\*
   -  assign netmask. This must match the netmask of the subnet the
      deployer will use to access the management port of the switch.
   -  default gateway
   -  Primary DNS server
   -  Domain name
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

      -  login to the switch
      -  enable
      -  configure terminal
      -  show vlan (note those vlans that include the ports of the nodes
         to be included in the new cluster)
      -  remove those vlans or remove those ports from existing vlans

         -  no vlan n

   -  Save config (In switch config mode: *configuration write* for
      Mellanox switches *copy running-config startup-config* for Lenovo
      switches (*write* works for G8052, G70XX). Consult vendor
      documentation.)::
	  
        Note that the management ports for the data and management switches
        in your cluster must all be in the same subnet. It is recommended 
        that the subnet used for switch management be a private subnet 
        which exists on the cluster management switches. If an external 
        network is used to access the management interfaces of your cluster 
        switches, insure that you have a route from the deployment 
        container to the switch management interfaces.  Generally this is 
        handled automatically when Linux creates the deployer container.

-  Configure Management switch(es) (for out of box installation, it is
   usually necessary to configure the switch using a serial connection.
   See the switch installation guide. For additional info on Lenovo G8052 specific
   commands, see Appendix G.)

   -  assign hostname
   -  create a vlan for use in accessing the management interfaces of your
      switches.  This must match the vlan specified by the "vlan-mgmt-network:" 
      key in your cluster configuration (config.yml) file::
	    
        en
        conf t
        vlan 16   (example vlan.)
		
   -  assign a static ip address, netmask and gateway address to a management interface. 
      This must match the address specified in
      the config.yml file (keyname: ipaddr-mgmt-switch:) and be in a
      *different* subnet than your cluster management subnet. Place this
      interface in the above created vlan::
  
        interface ip 1
        ip address 192.168.16.5    (example ip address)
        ip netmask 255.255.255.0   (example netmask)
        vlan 16
        enable
        exit
        ip gateway 1 address 192.168.16.1  (example ip address)
        ip gateway 1 enable
		
   -  admin password. This must match the password specified in the
      config.yml file (keyword: password-mgmt-switch:). Note that all
      management switches in the cluster must have the same userid and
      password.
   -  disable spanning tree (for Lenovo switches *enable, configure
      terminal, spanning-tree mode disable*)
   -  enable SSH login. *(ssh enable)*
	
   -  Put the port used to connect to the deployer node (the node running 
      Cluster Genesis) into trunk mode and add the above created vlan to that trunk::
	  
	    interface port 46  (example port #)
		switchport mode trunk
		trunk allowed vlan 1,16
		exit
		
	  
   -  Save the config (For Lenovo switches, enter config mode 
      then; *copy running-config startup-config or write.*  
      For additional information, consult vendor documentation)


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

-  Install Ununtu 14.04LTS or 16.04LTS to the deployer node. Insure
   SSH login is enabled.
-  Optionally, assign a static, public ip address to the BMC port to
   allow external control of the deployer node.
-  login into the deployer and install the vim, vlan and bridge-utils
   packages::

     $ sudo apt-get update
     $ sudo apt-get install vim vlan bridge-utils



**Note**: the port used to access the management switch (ie eth0) must
also be defined in /etc/network/interfaces (Ubuntu) or the ifcfg-eth0
file (Red Hat).

ie::

  auto eth0
  iface eth0 inet manual
