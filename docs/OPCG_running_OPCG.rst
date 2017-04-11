.. highlight:: none

Running the OpenPOWER Cluster Configuration Software
====================================================

Installing and Running the Genesis code. Step by Step Instructions
------------------------------------------------------------------

#.  Verify that all the steps in section `3.2 <#anchor-5>`__ `Setting up
    the Deployer Node <#anchor-5>`__ have been executed
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


#. copy your config.yml file to the ~/cluster-genesis directory (see
   section `4 <#anchor-4>`__ `Creating the config.yml
   File <#anchor-4>`__ for how to create the config.yml file)
#. copy any needed os image files (iso format) to the
   ~/cluster-genesis/os\_images directory.
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

   - Cycle power to the cluster nodes. BMC ports should boot and obtain
     an IP address from the deployer node.
   - Use ipmitool run as root local to each node; ipmitool bmc reset warm OR
     ipmitool mc reset warm depending on server
   - Use ipmitool remotely. (this assumes a known ip address already
     exists on the BMC interface)::

        ipmitool -I lanplus -U <username> -P <password> -H <bmc ip address> mc reset cold

   If necessary, use one of the following options to configure the BMC
   port to use DHCP;

   -  From a local console, reboot the system from the host OS, use the
      UEFI/BIOS setup menu to configure the BMC network configuration to
      DHCP, save and exit.
   -  use IPMItool to configure BMC network for DHCP and reboot the BMC


#. To deploy operating systems to your cluster nodes::

      $ gen deploy

#. This process can take as little as 30 minutes to several hours depending on
   on the size of the cluster and the complexity of the deployment.

   - To monitor progress of the deployment, open an additional terminal session
     into the deployment node and run the gen program with a status request.::

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
the BMC and PXE ports and initialize Cobbler to assign specific addresses to those MAC addresses.

After Genesis has assigned IP addresses to the PXE ports of all cluster nodes, it will display a list of
all nodes.  Genesis will wait up to 30 minutes for the PXE ports of all cluster nodes to
reset and obtain an IP address.  After 30 minutes, if there are nodes which have
still not requested a DHCP address, Genesis will pause to give you an opportunity to make fixes.

After all BMC and PXE ports have been discovered Genesis will begin operating system provisioning.

#. Introspection

If introspection is enabled then all client systems will be booted into the
in-memory OS with ssh enabled. One of the last tasks of this phase of Cluster 
Genesis will print a table of all introspection hosts, including their
IP addresses and login / ssh private key credentials. This list is maintained
in the 'cluster-genesis/playbooks/hosts' file under the 'introspections' group.
Genesis will pause after the introspection OS deployement to allow for customized 
updates to the cluster nodes.  Use ssh (future: or Ansible) to run custom scripts 
on the client nodes.

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

Cluster Genesis will generate an inventory file (inventory.yml) in
the /home/deployer/cluster-genesis directory in the container.
To view the inventory file (future)::

     $ gen inventory

**Configuring networks on the cluster nodes**

After completion of OS installation, Genesis performs several additional activities such
as setting up networking on the cluster nodes, setup SSH keys and copy to cluster nodes,
and configure the data switches. From the host namespace, execute::

   $ gen post-deploy

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
