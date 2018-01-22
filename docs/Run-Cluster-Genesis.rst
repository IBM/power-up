.. highlight:: none

Running the OpenPOWER Cluster Configuration Software
====================================================

Installing and Running the Genesis code. Step by Step Instructions
------------------------------------------------------------------

#.  Verify that all the steps in section `4 <#anchor-5>`__ `Prerequisite Hardware Setup
    <#anchor-5>`__ have been executed.  Genesis can not run if addresses have not been configured
    on the cluster switches and recorded in the config.yml file.
#.  login to the deployer node.
#.  Install git

    - Ubuntu::

        $ sudo apt-get install git

    - RHEL::

        $ sudo yum install git

#.  From your home directory, clone Cluster Genesis::

      $ git clone https://github.com/open-power-ref-design-toolkit/cluster-genesis

#.  Install the remaining software packages used by Cluster Genesis and
    setup the environment::

      $ cd cluster-genesis
      $ ./scripts/install.sh

      (this will take a few minutes to complete)

      $ source scripts/setup-env

    **NOTE:** The setup-env script will ask for permission to add
    lines to your .bashrc file.  It is recommended that you allow this.
    These lines can be removed using the "tear-down" script.

#. If introspection is enabled then follow the instructions in
   `Building Necessary Config Files <Build-Introspection.rst#building-necessary-config-files>`_
   to set the 'IS_BUILDROOT_CONFIG' and 'IS_KERNEL_CONFIG' environment
   variables.
#. copy your config.yml file to the ~/cluster-genesis directory (see
   section `4 <#anchor-4>`__ `Creating the config.yml
   File <#anchor-4>`__ for how to create the config.yml file)
#. Copy any needed os image files (iso format) to the
   '/cluster-genesis/os\_images' directory. Symbolic links to image
   files are also allowed.
#. For RHEL iso images, create a kickstart file having the same name as
   your iso image but with an extension of .ks. This can be done by
   copying the supplied kickstart file located in the
   /cluster-genesis/os\_images/config directory. For example, if your
   RHEL iso is *RHEL-7.2-20151030.0-Server-ppc64le-dvd1.iso*, from within
   the */cluster-genesis/os\_images/config directory*::

      $ cp RHEL-7.x-Server.ks RHEL-7.2-20151030.0-Server-ppc64le-dvd1.ks

   (The cobbler-profile: key in your config.yml file should have a value
   of RHEL-7.2-20151030.0-Server-ppc64le-dvd1 (no .ks extension)*

   NOTE:
    Before beginning the next step, be sure all BMCs are configured to obtain a
    DHCP address then reset (reboot) all BMC interfaces of your cluster nodes.  As the BMCs reset,
    the Cluster Genesis DHCP server will assign new addresses to the BMCs of all cluster nodes.

   One of the following options can be used to reset the BMC interfaces;

   - Cycle power to the cluster nodes. BMC ports should boot and wait to obtain
     an IP address from the deployer node.
   - Use ipmitool run as root local to each node; ipmitool bmc reset warm OR
     ipmitool mc reset warm depending on server
   - Use ipmitool remotely such as from the deployer node. (this assumes a known
     ip address already exists on the BMC interface)::

        ipmitool -I lanplus -U <username> -P <password> -H <bmc ip address> mc reset cold

   If necessary, use one of the following options to configure the BMC
   port to use DHCP;

   -  From a local console, reboot the system from the host OS, use the
      UEFI/BIOS setup menu to configure the BMC network configuration to
      DHCP, save and exit.
   -  use IPMItool to configure BMC network for DHCP and reboot the BMC

   Most of Genesis' capabilities are accessed using the 'gen' program. For a
   complete overview of the gen program, see Appendix A.

#. To deploy operating systems to your cluster nodes::

      $ gen deploy

   *Note*: If running with passive management switch(es) follow special
   instructions in :ref:`deploy-passive <deploy-passive>` instead.

#. This will create the management neworks, install the container that runs most of the Genesis
   functions and then optionally launch the introspection OS and then install OS's on the cluster nodes.
   This process can take as little as 30 minutes or as much as mutliple hours depending on
   the size of the cluster, the capabilities of the deployer and the complexity of the deployment.

   - To monitor progress of the deployment, open an additional terminal session
     into the deployment node and run the gen program with a status request.  (During install, you
     must allow Genesis to make updates to your .bashrc file in order to run gen functions
     from another terminal session)::

      $ gen status


   After several minutes Cluster Genesis will have initialized and should display a list of cluster
   nodes which have obtained BMC addresses.  Genesis will wait up to 30 minutes for the BMCs of all
   cluster nodes to reset and obtain an IP address.  After 30 minutes, if there are nodes which have
   still not requested a DHCP address, Genesis will pause to give you an opportunity to make fixes.
   If any nodes are missing, verify cabling and verify the config.yml file. If
   necessary, recycle power to the missing nodes. See "Recovering from Genesis Issues" in the
   appendices for additional debug help.  You can monitor which nodes have obtained ip
   addresses, by executing the following from another window::

      $ gen status

   After Genesis completes the assignment of DHCP addresses to the cluster nodes BMC ports,
   Genesis will interrogate the management switches and read the MAC addresses associated with
   the BMC and PXE ports and initialize Cobbler to assign specific IP addresses to the interfaces
   holding those MAC addresses.

   After Genesis has assigned IP addresses to the BMC ports of all cluster nodes, it will display a list of
   all nodes.  Genesis will wait up to 30 minutes for the PXE ports of all cluster nodes to
   reset and obtain an IP address.  After 30 minutes, if there are nodes which have
   still not requested a DHCP address, Genesis will pause to give you an opportunity to make fixes.

   After all BMC and PXE ports have been discovered Genesis will begin operating system deployment.

#. Introspection

   If introspection is enabled then all client systems will be booted into the
   in-memory OS with ssh enabled. One of the last tasks of this phase of Cluster
   Genesis will print a table of all introspection hosts, including their
   IP addresses and login / ssh private key credentials. This list is maintained
   in the 'cluster-genesis/playbooks/hosts' file under the 'introspections' group.
   Genesis will pause after the introspection OS deployement to allow for customized
   updates to the cluster nodes.  Use ssh (future: or Ansible) to run custom scripts
   on the client nodes.

   .. _deploy-passive-continue:

#. To continue the Genesis process, press enter and/or enter the sudo password

   Again, you can monitor the progress of operating system installation from an
   additional SSH window::

     $ gen status

   It will usually take several minutes for all the nodes to load their OS.
   If any nodes do not appear in the cobbler status, see "Recovering from
   Genesis Issues" in the Appendices

   Genesis creates logs of it's activities. A file (log.txt) external to the Genesis container
   is written in the cluster-genesis directory.  This can be viewed::

     $ gen log

   An additional log file is created within the deployer container.
   This log file can be viewed::

     $ gen logc


**Configuring networks on the cluster nodes**

*Note*: If running with passive data switch(es) follow special instructions in
:ref:`post-deploy-passive <post-deploy-passive>` instead.

After completion of OS installation, Genesis performs several additional activities such
as setting up networking on the cluster nodes, setup SSH keys and copy to cluster nodes,
and configure the data switches. From the host namespace, execute::

   $ gen post-deploy

If data switches are configured with MLAG verify

  * The switch IPL ports are disabled or are not plugged in.
  * No port channels are defined.


Passive Switch Mode Special Instructions
----------------------------------------

.. _deploy-passive:

**Deploying operating systems to your cluster nodes with passive management
switches**

When prompted, it is advisable to clear the mac address table on the management
switch(es).::

    $ gen deploy-passive

When prompted, write each switch MAC address table to file in
'cluster-genesis/passive'. The files should be named to match the unique
values set in the 'config.yml' 'ipaddr-mgmt-switch' dictionary. For example,
take the following 'ipaddr-mgmt-switch' configuration::

    ipaddr-mgmt-switch:
        rack1: passive_mgmt_rack1
        rack2: passive_mgmt_rack2

The user would need to write two files:
	1. 'cluster-genesis/passive/passive_mgmt_rack1'
	2. 'cluster-genesis/passive/passive_mgmt_rack2'

If the user has ssh access to the switch management interface writing the MAC
address table to file can easily be accomplished by redirecting stdout. Here is
an example of the syntax for a Lenovo G8052::

    $ ssh <mgmt_switch_user>@<mgmt_switch_ip> \
    'show mac-address-table' > ~/cluster-genesis/passive/passive_mgmt_rack1

Note that this command would need to be run for each individual mgmt switch,
writing to a seperate file for each. It is recommended to verify each file has
a complete table for the appropriate interface configuration and only one mac
address entry per interface.

See :ref:`MAC address table file formatting rules <mac-table-file-rules>` below.

After writing MAC address tables to file press enter to continue with OS
installation. :ref:`Resume normal instructions <deploy-passive-continue>`.

If deploy-passive fails due to incomplete MAC address table(s) use the
following command to reset all servers (power off / set bootdev pxe / power on)
and attempt to collect MAC address table(s) again when prompted::

    $ gen deploy-passive-retry

.. _post-deploy-passive:

**Configuring networks on the cluster nodes with passive data switches**

When prompted, it is advisable to clear the mac address table on the data
switch(es). This step can be skipped if the operating systems have just been
installed on the cluster nodes and the mac address timeout on the switches is
short enough to insure that no mac addresses remain for the data switch ports
connected to cluster nodes. If in doubt, check the acquired mac address file
(see below) to insure that each data port for your cluster has only a single
mac address entry.::

    $ gen post-deploy-passive

When prompted, write each switch MAC address table to file in
'cluster-genesis/passive'. The files should be named to match the unique
values set in the 'config.yml' 'ipaddr-data-switch' dictionary. For example,
take the following 'ipaddr-data-switch' configuration::

    ipaddr-data-switch:
        base-rack: passive1
        rack2: passive2
        rack3: passive3

The user would need to write three files:
	1. 'cluster-genesis/passive/passive1'
	2. 'cluster-genesis/passive/passive2'
	3. 'cluster-genesis/passive/passive3'

If the user has ssh access to the switch management interface writing the MAC
address table to file can easily be accomplished by redirecting stdout. Here is
an example of the syntax for a Mellanox SX1400::

    $ ssh <data_switch_user>@<data_switch_ip> \
    'cli en show\ mac-address-table' > ~/cluster-genesis/passive/passive1

Note that this command would need to be run for each individual data switch,
writing to a seperate file for each. It is recommended to verify each file has
a complete table for the appropriate interface configuration and only one mac
address entry per interface.

See :ref:`MAC address table file formatting rules <mac-table-file-rules>` below.

.. _mac-table-file-rules:

**MAC Address Table Formatting Rules**

Each file must be formatted according to the following rules:

    * MAC addresses and ports are listed in a tabular format.
        - Columns can be in any order
        - Additional columns (e.g. vlan) are OK as long as a header is
          provided.
    * If a header is provided and it includes the strings "mac address" and
      "port" (case insensitive) it will be used to identify column positions.
      Column headers must be delimited by at least two spaces. Single spaces
      will be considered a continuation of a single column header (e.g. "mac
      address" is one column, but "mac address  vlan" would be two).
    * If a header is not provided then only MAC address and Port columns are
      allowed.
    * MAC addresses are written as (case-insensitive):
      	- Six pairs of hex digits delimited by colons (:) [e.g. 01:23:45:67:89:ab]
      	- Six pairs of hex digits delimited by hyphens (-) [e.g. 01-23-45-67-89-ab]
      	- Three quads of hex digits delimited by periods (.) [e.g. 0123.4567.89ab]
    * Ports are written either as:
        - An integer
        - A string with a "/". The string up to and including the "/" will be
          removed. (e.g. "Eth1/5" will be saved as "5").

Both Lenovo and Mellanox switches currently supported by Cluster Genesis follow
these rules. An example of a user generated "generic" file would be::

    mac address        Port
    0c:c4:7a:20:0d:22    38
    0c:c4:7a:76:b0:9b    19
    0c:c4:7a:76:b1:16    9
    0c:c4:7a:76:c8:ec    37
    40:f2:e9:23:82:ba    18
    40:f2:e9:23:82:be    17
    40:f2:e9:24:96:5a    22
    40:f2:e9:24:96:5e    21
    5c:f3:fc:31:05:f0    13
    5c:f3:fc:31:06:2a    12
    5c:f3:fc:31:06:2c    11
    5c:f3:fc:31:06:ea    16
    5c:f3:fc:31:06:ec    15
    6c:ae:8b:69:22:24    2
    70:e2:84:14:02:92    5
    70:e2:84:14:0f:57    1


SSH Keys
--------

The OpenPOWER Cluster Genesis Software will generate a passphrase-less SSH
key pair which is distributed to
each node in the cluster in the /root/.ssh directory. The public key is
written to the authorized\_keys file in the /root/.ssh directory and
also to the /home/userid-default/.ssh directory. This key pair can be
used for gaining passwordless root login to the cluster nodes or
passwordless access to the userid-default. On the deployer node, the
keypair is written to the ~/.ssh directory as id\_rsa\_ansible-generated
and id\_rsa\_ansible-generated.pub. To login to one of the cluster nodes
as root from the deployer node::

    ssh -i ~/.ssh/id_rsa_ansible-generated root@a.b.c.d

As root, you can log into any node in the cluster from any other node in
the cluster as::

    ssh root@a.b.c.d

where a.b.c.d is the ip address of the port used for pxe install. These
addresses are stored under the keyname *ipv4-pxe* in the inventory file.
The inventory file is stored on every node in the cluster at
/var/oprc/inventory.yml. The inventory file is also stored on the
deployer in the deployer container in the /home/deployer/cluster-genesis
directory.

Note that you can also log into any node in the cluster using the
credentials specified in the config.yml file (keynames *userid-default*
and *password-default*)
