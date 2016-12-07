===============
Cluster Genesis
===============


Introduction
============
Cluster Genesis simplifies configuration of clusters of baremetal
OpenPOWER servers running Linux. It leverages widely used open source tools such
as Cobbler, Ansible and Python. Because it relies solely on industry standard
protocols such as IPMI and PXE boot, hybrid clusters of OpenPOWER and x86 nodes
can readily be supported. Currently Genesis supports Ethernet networking with
separate data and management networks. Genesis can configure simple flat
networks for typical HPC environments or more advanced networks with VLANs and
bridges for OpenStack environments. Genesis also configures the switches in the
cluster. Currently Mellanox SX1410 is supported for the data network and the
Lenovo G8052 is supported for the management network. Supported hardware
includes OpenPOWER and x86 servers, and OS distributions such as Ubuntu, CentOS,
and RHEL.


Overview
========
Cluster Genesis is designed to be easy to use. If you are implementing one of the
supported architectures with supported hardware, Genesis eliminates the need for
custom scripts or programming. It does this via a configuration file
(config.yml) which drives the cluster configuration. The configuration file is a
YAML text file which the user edits. Example YAML files are included. The
configuration process is driven from a "deployer" node which does not need to
remain in the cluster when finished. The process is as follows:

#. Rack and cable the hardware.
#. Initialize hardware.

   * Initialize switches with static ip address, userid and password.
   * Ensure that all cluster compute nodes are set to obtain a DHCP address on
     their BMC ports.
#. Install the Cluster Genesis software on the deployer node.
#. Edit an existing config.yml file.
#. Run the Cluster Genesis software.
#. Power on the cluster client (management, compute and storage) nodes.

Cluster Genesis generates a YAML formatted inventory file which can subsequently
be used by other applications.


Project Resources
=================
For additional instructions and developer resources:

* Wiki: https://github.com/open-power-ref-design/cluster-genesis/wiki
* IRC:  #cluster-genesis channel on freenode.net


Deployer Node Installation
==========================

::

$ sudo apt update; sudo apt install git
$ git clone https://github.com/open-power-ref-design/cluster-genesis.git
$ cd cluster-genesis
$ ./scripts/install.sh
$ source scripts/setup-env
$ export ANSIBLE_HOST_KEY_CHECKING=False
$ cd playbooks


Deployer Node Network Configuration
===================================
Create a network bridge named "br0" with port connected to management
network (e.g. 192.168.3.0/24).

Below is an example interface defined in the local
"/etc/network/interfaces" file. Note that "p1p1" is the name of the
interface connected to the management network.

::

    auto br0
    iface br0 inet static
        address 192.168.3.3
        netmask 255.255.255.0
        bridge_ports p1p1


Create LXC Container
====================
LXC container hosts features such as provisioning scripts, cluster
configurations data, cobbler instance, DHCP server, and HTTP server.

::

$ ansible-playbook -i hosts lxc-create.yml -K


Configure LXC Container and Provision Client Nodes
==================================================
::

$ ansible-playbook -i hosts install.yml -K


Configure Cluster Node Networks
===============================
After the OS installation, the ansible playbooks below will setup the networks
on the client nodes as defined in the config.yml file.

::

$ ansible-playbook -i ../scripts/python/yggdrasil/inventory.py gather_mac_addresses.yml -u root --private-key=~/.ssh/id_rsa_ansible-generated
$ ansible-playbook -i ../scripts/python/yggdrasil/inventory.py configure_operating_systems.yml -u root --private-key=~/.ssh/id_rsa_ansible-generated


Authors
=======
Cluster Genesis is sponsored by IBM POWER Systems Development.
