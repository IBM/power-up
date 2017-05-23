.. highlight:: none

Appendix - I Using the 'tear-down' Program
==========================================


The 'tear-down' program allows for select 'tear down' of the Genesis
environment on the deployer node and cluster switches. It is primarily used
when redeploying your cluster for test purposes, after taking corrective action
after previous deployment failures or for removing the Cluster Genesis environment
from the deployer node.

tear-down is completely interactive and only acts when you respond 'y' to prompts.

Usage::

	tear-down

There are currently no arguments or options.

The tear-down program can perform the following
functions;

    - Backup the config.yml file.  Backed up to ~/configbak directory.
      Config.yml files are date/time stamped.
    - Backup the os-images directory
    - Remove the Cluster Genesis created management interface from the
      management switch.
    - Remove the Cluster Genesis created bridges from the deployer node.
    - Remove the Genesis container.  Removes the containers SSH key fom the
      deployers known_host file.
    - Remove the Cluster Genesis software and the directory it is installed in.
    - Remove entries made to the .bashrc file and undo changes made to the
      $PATH environment variable.
    - Remove the SSH keys for cluster switches from the deployer known_host file.

For a typical redeploy where the Cluster Genesis software does not need
updating, you should remove the cluster genesis container and it's associated
bridges.  You should also allow removal of all SSH keys from the known_hosts file.
