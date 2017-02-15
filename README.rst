===============
Cluster Genesis
===============


Introduction
============

Cluster Genesis simplifies configuration of clusters of baremetal OpenPOWER and
x86 servers running Linux. It leverages widely used open source tools such as
Cobbler, Ansible and Python. Because it relies solely on industry standard
protocols such as IPMI and PXE boot, hybrid clusters of OpenPOWER and x86 nodes
can readily be supported. Currently Genesis supports Ethernet networking with
separate data and management networks. Genesis can configure simple flat
networks for typical HPC environments or more advanced networks with VLANs and
bridges for OpenStack environments. Genesis also configures the switches in the
cluster. Currently Mellanox SX1410 is supported for the data network and the
Lenovo G8052 is supported for the management network. Supported hardware
includes OpenPOWER and x86 servers, and OS distributions such as Ubuntu,
CentOS, and RHEL.


Overview
========

Cluster Genesis is designed to be easy to use. If you are implementing one of
the supported architectures with supported hardware, Genesis eliminates the
need for custom scripts or programming. It does this via a configuration file
(config.yml) which drives the cluster configuration. The configuration file is
a YAML text file which the user edits. Example YAML files are included. The
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

Cluster Genesis generates a YAML formatted inventory file which can
subsequently be used by other applications.


Project Resources
=================

For additional instructions and developer resources:

* `User's Guide <http://cluster-genesis.readthedocs.io>`_ at 'Read the Docs'
* `Developer's Guide <docs/OPCG_dev_guide.rst>`_
* IRC:  #cluster-genesis channel on freenode.net


Authors
=======

Cluster Genesis is sponsored by IBM POWER Systems Development.
