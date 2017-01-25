.. highlight:: none 

Running the OpenPOWER Cluster Configuration Software
====================================================

Installing and Running the Genesis code. Step by Step Instructions
------------------------------------------------------------------

#.  Verify that all the steps in section `3.2 <#anchor-5>`__ `Setting up
    the Deployer Node <#anchor-5>`__ have been executed
#.  login to the deployer node.
#.  Export the following environment variable::
    
      $ export GIT_SSL_NO_VERIFY=1
    
#.  Enable the root account and change the root password to 
    passw0rd (note that the alpha "o" is replaced with numeric 0)::

      $ sudo passwd root 
       
       (enter passw0rd twice when prompted. This can be disabled 
       again and password deleted when genesis completes. 
       ie sudo passwd -dl root)

#.  Install git::

      $ sudo apt-get install git
    
#.  From your home directory, clone Cluster Genesis::

      $ git clone https://github.com/open-power-ref-design/cluster-genesis
      
#.  Install the remaining software packages used by Cluster Genesis and 
    setup the environment::
    
      $ cd cluster-genesis
      $ ./scripts/install.sh
     
      (this will take a few minutes to complete)
      
      $ source scripts/setup-env
      
    **NOTE:** anytime you leave and restart
    your shell session, you need to re-execute the set-env script.
    Alternately, (recommended) add the following to your .bashrc file;
    *PATH=~/cluster-genesis/deployenv/bin:$PATH* 
    
    ie::
    
      $ echo "PATH=~/cluster-genesis/deployenv/bin:\$PATH" >> ~/.bashrc

#. copy your config.yml file to the ~/cluster-genesis directory (see
   section `4 <#anchor-4>`__ `Creating the config.yml
   File <#anchor-4>`__ for how to create the config.yml file)
#. copy any needed os image files (iso format) to the
   ~/cluster-genesis/os\_images directory.
#. For RHEL iso images, create a kickstart file having the same name as
   your iso image but with an extension of .ks. This can be done by
   copying the supplied kickstart file located in the
   /cluster-genesis/os\_images/config directory. For expample, if your
   RHEL iso is *RHEL-7.2-20151030.0-Server-ppc64le-dvd1.iso*, from within
   the */cluster-genesis/os\_images/config directory*::

      $ cp RHEL-7.2-Server-ppc64le.ks RHEL-7.2-20151030.0-Server-ppc64le-dvd1.ks
   
   (The cobbler-profile: key in your config.yml file should have a value
   of RHEL-7.2-20151030.0-Server-ppc64le-dvd1 (no .ks extension)*
#. Make the ~/cluster-genesis/playbooks directory the current working directory::
     
      $ cd ~/cluster-genesis/playbooks/
      
#. Create the container for Genesis to run in. This typically takes several minutes to run::

      $ ansible-playbook -i hosts lxc-create.yml -K

#. verify that you can access the management interfaces of the
   management switch(es) (ie ping) from within
   the newly created container.

   - To see the name of the created container::

      $ sudo lxc-ls

   - To access the container::

      $ sudo lxc-attach -n containername
      $ ping -c3 192.168.16.5 
      (Example address.  This should match the address assigned to the
      management interface of one of your switches.  Note that the above
      commands access the container as root.)

   NOTE: 
       Before beginning the next step, be sure all BMCs are configured to obtain a 
       DHCP address then reset (reboot) all BMC interfaces of your cluster nodes.  As the BMCs reset, 
       the Cluster Genesis DHCP server will assign new addresses to the BMCs of all cluster nodes.
  
   One of the following options can be used to reset the BMC interfaces;

   - Cycle power to the cluster nodes. BMC ports should boot and optain
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
	  
	  
#. To begin genesis of your cluster, from the cluster-genesis/playbooks directory run::

      $ ansible-playbook -i hosts install.yml -K
      NOTE that this will typically take 30 minutes or more to run depending on the size of your cluster.

   After several minutes Cluster Genesis will have initialized and should display a list of cluster 
   nodes which have obtained BMC addresses.  Genesis will wait up to 30 minutes for the BMCs of all 
   cluster nodes to reset and obtain an IP address.  You can monitor which nodes have obtained ip 
   addresses, by executing the following from another window within the container::

      $ cat /var/lib/misc/dnsmasq.leases
	
   Verify that all cluster nodes appear in the list. 
	  
   If any nodes are missing, verify cabling and verify the config.yml file. If
   necessary, recycle power to the missing nodes. See "Recovering from Genesis Issues" in the 
   appendices for additional debug help. 


After Genesis completes the assignment of DHCP addresses to the cluster nodes BMCS ports,
Genesis will interogate the management switches and read the MAC addresses associated with
the BMC and PXE ports and initialize Cobbler to assign specific addresses to those MAC addresses.

After Genesis has assigned IP addresses to the PXE ports of all cluster nodes, it will display a list of
all nodes.  Genesis will wait up to 30 minutes for the PXE ports of all cluster nodes to 
reset and obtain an IP address.


After the command prompt returns, you can monitor the progress of 
operating system installation as follows:

#. First, login to the genesis container.  To get the login information::

     $ grep "^deployer" ~/cluster-genesis/playbooks/hosts
     deployer ansible_user=deployer ansible_ssh_private_key_file=/home/ubuntu/.ssh/id_rsa_ansible-generated ansible_host=192.168.0.2*
     $ ssh -i ~/.ssh/id_rsa_ansible-generated deployer@192.168.0.2
	 (example ip address.  Replace with the ip address for your cluster)

#. From withing the container, execute the following command within the /home/deployer/cluster-genesis
   directory to see progress/status of operating system installation::  
   
   $ sudo cobbler status

It will usually take several minutes for all the nodes to load their OS.
If any nodes do not appear in the cobbler status, see "Recovering from 
Genesis Issues" in the Appendices

Genesis creates a log of it's activities. This file is written in the
deployer container to /home/deployer/cluster-genesis/log.txt

The cluster Genesis will generate an inventory file (inventory.yml) in
the /var/oprc directory of the host namespace and in the
/home/deployer/cluster-genesis directory in the container.

**Configuring networks on the cluster nodes**

After completion of OS installation, the following ansible playbooks 
can be run to setup the networks on cluster nodes as defined in the network template
and compute template sections of the config.yml file. SSH keys are also
generated and copied to each cluster node. From the host namespace, in the 
*~/cluster-genesis/playbooks* directory execute::

   $ ansible-playbook -i ../scripts/python/yggdrasil/inventory.py ssh_keyscan.yml -u root --private-key=~/.ssh/id_rsa_ansible-generated
   $ ansible-playbook -i ../scripts/python/yggdrasil/inventory.py gather_mac_addresses.yml -u root --private-key=~/.ssh/id_rsa_ansible-generated
   $ ansible-playbook -i ../scripts/python/yggdrasil/inventory.py configure_operating_systems.yml -u root --private-key=~/.ssh/id_rsa_ansible-generated



SSH Keys
--------

The OpenPOWER Cluster Genesis Software will generate a passphrase-less SSH key pair which is distributed to
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
