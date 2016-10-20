----

File: lxc-create.yml
====================
Play: lxc-create.yml
--------------------
* Hosts: localhost

#. Print local project path \[debug]
#. Install aptitude \[apt]
#. Update apt cache and upgrade (safe) \[apt]
#. Install LXC \[apt]
#. Install liblxc1 \[apt]
#. Install python-lxc \[apt]
#. Update ~/.config/lxc/default.conf \[lineinfile]
#. Make backup of /etc/lxc/lxc-usernet \[copy]
#. Update /etc/lxc/lxc-usernet \[lineinfile]
#. Register management network subnet address \[shell: grep ipaddr-mgmt-network {{ config_local }} | awk '{print $2}']
#. Update group_vars/all container_mgmt_subnet \[replace]
#. Update lxc.conf container mgmt ipv4 address \[replace]
#. Create private/public ssh key pair \[user]
#. Create LXC deployment container \[lxc_container]
#. Pause 5 seconds \[pause]
#. Register container internal ip address \[command: lxc-info -n {{ container_name }} -iH]
#. Print container IP information \[debug]
#. Update "installer" host with ssh private key. \[replace]
#. Update "installer" host with container internal IP address. \[replace]
#. Update "deployer" host with ssh private key. \[replace]
#. Update "deployer" host with container management network IP address. \[replace]

----

File: install.yml
=================
Include: lxc-update.yml
-----------------------
Play: lxc-update.yml
--------------------
* Hosts: localhost \[gather_facts: True]

#. Download OS installer images from IBM GSA \[get_url]

* Hosts: installer

#. Print local scripts/config paths \[debug]
#. Update apt cache and upgrade (safe) \[apt]
#. Install distro packages \[apt]
#. Install python pip packages \[pip]
#. Create project root directory \[file]
#. Create python virtual environment \[command: virtualenv --no-wheel --system-site-packages {{ venv_path }}]
#. Activate python venv and install pip packages \[command: /bin/bash -c " source {{ venv_path }}/bin/activate && pip install --ignore-installed pyaml orderedattrdict pysnmp pyghmi paramiko && deactivate"]
#. Copy config file into deployment container \[copy]
#. Copy scripts into deployment container \[copy]
#. Copy OS images and configs into deployment container \[copy]
#. Create log file \[file]


Include: container/cobbler/cobbler_install.yml
----------------------------------------------
Play: Gather facts from localhost
---------------------------------
* Hosts: localhost \[gather_facts: True]

Play: container/cobbler/cobbler_install.yml
-------------------------------------------
* Hosts: installer

#. Install aptitude to enable apt upgrade safe  \[apt]
#. Update apt cache & upgrade packages (safe) \[apt]
#. Install software packages \[apt]
#. Clone Cobbler github repo \[git]
#. Run Cobbler make install \[command: make install chdir="/home/{{ user }}/cobbler"]
#. Create cobbler symlink \[file]
#. Create tftp root directory \[file]
#. Save original /etc/cobbler/dnsmasq.template file \[copy]
#. Set IP address range to use for unrecognized DHCP clients \[replace]
#. Configure dnsmasq to enable TFTP server \[lineinfile]
#. Save original /etc/cobbler/modules.conf file \[copy]
#. Configure Cobbler to use dnsmasq for DHCP and DNS services \[replace]
#. Copy cobbler.conf into apache2/conf-available \[copy]
#. Copy cobbler_web.conf into apache2/conf-available \[copy]
#. Enable cobbler & cobbler_web apache2 configuration \[command: /usr/sbin/a2enconf cobbler cobbler_web]
#. Enable proxy apache2 configuration \[command: /usr/sbin/a2enmod proxy]
#. Enable proxy_http apache2 configuration \[command: /usr/sbin/a2enmod proxy_http]
#. Save original /usr/local/share/cobbler/web/settings.py file \[copy]
#. Generate 100 random characters to use as secret key in /usr/local/share/cobbler/web/settings.py \[command: python -c 'import re;from random import choice; import sys; sys.stdout.write(re.escape("".join([choice("abcdefghijklmnopqrstuvwxyz0123456789^&*(-_=+)") for i in range(100)])))']
#. Set secret key in /usr/local/share/cobbler/web/settings.py \[replace]
#. Save original /etc/apache2/conf-enabled/cobbler.conf file \[copy]
#. Save original /etc/apache2/conf-enabled/cobbler_web.conf file \[copy]
#. Apache2 config \[lineinfile]
#. Apache2 config \[replace]
#. Chown www-data /var/lib/cobbler/webui_sessions \[file]
#. Save original /etc/cobbler/settings file \[copy]
#. Update cobbler server settings \[replace]
#. Save original /etc/cobbler/pxe/pxedefault.template file \[copy]
#. Set PXE timeout to maximum \[replace]
#. Save original /var/lib/cobbler/snippets/kickstart_done file \[copy]
#. Fix line break escape in kickstart_done snippet \[replace]
#. Copy authorized_keys ssh key file to web repo directory \[copy]
#. Restart cobblerd service \[service]
#. Restart apache2 service \[service]
#. Update boot-loader files \[command: /usr/local/bin/cobbler get-loaders]
#. Update cobbler list of OS signatures \[command: /usr/local/bin/cobbler signature update]
#. Run cobbler sync \[command: /usr/local/bin/cobbler sync]
#. Restart cobblerd service (again) \[service]
#. Restart apache2 service (again) \[service]
#. Restart dnsmasq service \[service]
#. Set cobblerd service to start on boot \[service]


Include: pause.yml message="Please reset BMC interfaces to obtain DHCP leases. Press <enter> to continue"
---------------------------------------------------------------------------------------------------------
Play: Pause
-----------
* Hosts: localhost

#. Pause (seconds) \[pause]
#. Pause (minutes) \[pause]
#. Pause (wait for key press) \[pause]


Include: container/set_data_switch_config.yml log_level=info
------------------------------------------------------------
Play: container/set_data_switch_config.yml
------------------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/set_data_switch_config.py {{ config }} {{ log_level }}]


Include: container/inv_add_switches.yml log_level=info
------------------------------------------------------
Play: container/inv_add_switches.yml
------------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/inv_add_switches.py {{ config }} {{ inventory }} {{ log_level }}]


Include: container/inv_add_ipmi_ports.yml log_level=info
--------------------------------------------------------
Play: container/inv_add_ipmi_ports.yml
--------------------------------------
* Hosts: deployer

#. \[command: awk '{system("ping -c 5 "$3)}' {{ dhcp_leases_file }}]
#. \[command: {{ python_executable }} {{ scripts_path }}/python/inv_add_ipmi_ports.py {{ config }} {{ inventory }} {{ dhcp_leases_file }} {{ log_level }}]


Include: container/ipmi_set_bootdev.yml log_level=info bootdev=network persistent=False
---------------------------------------------------------------------------------------
Play: container/ipmi_set_bootdev.yml
------------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/ipmi_set_bootdev.py {{ inventory }} {{ bootdev }} {{ persistent }} {{ log_level }}]


Include: container/ipmi_power_on.yml log_level=info
---------------------------------------------------
Play: container/ipmi_power_on.yml
---------------------------------
* Hosts: deployer

#. Power on all nodes \[command: {{ python_executable }} {{ scripts_path }}/python/ipmi_power_on.py {{ inventory }} {{ log_level }}]


Include: pause.yml minutes=5 message="Power-on Nodes"
-----------------------------------------------------
Play: Pause
-----------
* Hosts: localhost

#. Pause (seconds) \[pause]
#. Pause (minutes) \[pause]
#. Pause (wait for key press) \[pause]


Include: container/inv_add_ipmi_data.yml log_level=info
-------------------------------------------------------
Play: container/inv_add_ipmi_data.yml
-------------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/inv_add_ipmi_data.py {{ config }} {{ inventory }} {{ log_level }}]


Include: container/inv_add_pxe_ports.yml log_level=info
-------------------------------------------------------
Play: container/inv_add_pxe_ports.yml
-------------------------------------
* Hosts: deployer

#. \[command: awk '{system("ping -c 5 "$3)}' {{ dhcp_leases_file }}]
#. \[command: {{ python_executable }} {{ scripts_path }}/python/inv_add_pxe_ports.py {{ config }} {{ inventory }} {{ dhcp_leases_file }} {{ log_level }}]


Include: container/ipmi_power_off.yml log_level=info
----------------------------------------------------
Play: container/ipmi_power_off.yml
----------------------------------
* Hosts: deployer

#. Power off all nodes \[command: {{ python_executable }} {{ scripts_path }}/python/ipmi_power_off.py {{ inventory }} {{ log_level }}]


Include: container/inv_modify_ipv4.yml log_level=info
-----------------------------------------------------
Play: container/inv_modify_ipv4.yml
-----------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/inv_modify_ipv4.py {{ config }} {{ inventory }} {{ node_mgmt_ipv4_start }} {{ log_level }}]


Include: container/cobbler/cobbler_add_distros.yml
--------------------------------------------------
Play: Gather facts from localhost
---------------------------------
* Hosts: localhost \[gather_facts: True]

Play: container/cobbler/cobbler_add_distros.yml
-----------------------------------------------
* Hosts: deployer

#. Restore original /etc/cobbler/pxe/pxedefault.template file \[copy]
#. Register list of *.iso files \[find]
#. Register list of *.mini.iso files \[find]
#. Register list of *.seed files \[find]
#. Register list of *.list files \[find]
#. Register list of *.cfg files \[find]
#. Mount Distro installer images \[mount]
#. Copy distro images to http repo directory \[command: rsync -a /mnt/{{ item.path | basename | regex_replace('^(.*).iso$', '\1') }}/ /var/www/html/{{ item.path | basename | regex_replace('^(.*).iso$', '\1') }}/]
#. Copy "mini" netboot files to web repo directory \[command: rsync -a /mnt/{{ item.path | basename | regex_replace('^(.*).iso$', '\1') }}/install/ /var/www/html/{{ item.path | basename | regex_replace('^(.*).mini.iso$', '\1') }}/install/netboot/]
#. Register default user id \[shell: grep userid-default {{ config }} | awk '{print $2}']
#. Update preseed configurations with default user id \[replace]
#. Register default password \[shell: grep password-default {{ config }} | awk '{print $2}']
#. Update preseed configurations with default user password \[replace]
#. Copy preseed & kickstart configurations to cobbler kickstart directory \[copy]
#. Copy apt source lists to web repo directory \[copy]
#. Unmount distro installer images \[mount]
#. Call python "cobbler_add_distros.py" script to import distros and create default profiles \[command: {{ python_executable }} {{ scripts_path }}/python/cobbler_add_distros.py /var/www/html/{{ item.path | basename | regex_replace('^(.*)[.]iso$', '\1') }} {{ item.path | basename | regex_replace('^(.*)[.]iso$', '\1') }} {{ log_level }}]


Include: container/cobbler/cobbler_add_profiles.yml
---------------------------------------------------
Play: Gather facts from localhost
---------------------------------
* Hosts: localhost \[gather_facts: True]

Play: container/cobbler/cobbler_add_profiles.yml
------------------------------------------------
* Hosts: deployer

#. Register list of *.seed files \[shell: ls {{ project_path }}/os_images/config/*.seed]
#. Filter out default *.seed files \[shell: ls {{ project_path }}/os_images/{{ item | basename | regex_replace('^(.*)[.]seed$', '\1.iso') }} || echo True]
#. Read any associated *.kopts files \[shell: cat {{ project_path }}/os_images/config/{{ item.item | basename |regex_replace('^(.*)[.]seed$', '\1.kopts') }} || echo none]
#. Call python "cobbler_add_profiles.py" script to create additional profiles \[command: {{ python_executable }} {{ scripts_path }}/python/cobbler_add_profiles.py {{ item.0.item | basename | regex_replace('^(.*)[.].*[.]seed$', '\1') }} {{ item.0.item | basename | regex_replace('^(.*)[.]seed$', '\1') }} "{{ item.1.stdout }}" {{ log_level }}]


Include: container/cobbler/cobbler_add_systems.yml
--------------------------------------------------
Play: container/cobbler/cobbler_add_systems.yml
-----------------------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/cobbler_add_systems.py {{ config }} {{ inventory }} {{ log_level }}]


Include: container/inv_add_config_file.yml
------------------------------------------
Play: container/inv_add_config_file.yml
---------------------------------------
* Hosts: deployer

#. Append config.yml to inventory.yml \[shell: sed '/^---/d' {{ config }} >> {{ inventory }}]


Include: container/allocate_ip_addresses.yml
--------------------------------------------
Play: container/allocate_ip_addresses.yml
-----------------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/yggdrasil/allocate_ip_addresses.py --inventory {{ inventory }}]


Include: container/get_inv_file.yml dest=/var/oprc
--------------------------------------------------
Play: container/get_inv_file.yml (localhost)
--------------------------------------------
* Hosts: localhost

#. Ensure {{ dest }} directory exists \[file]

Play: container/get_inv_file.yml (deployer)
-------------------------------------------
* Hosts: deployer

#. Fetch inventory file from deployer \[fetch]


Include: container/ipmi_set_bootdev.yml log_level=info bootdev=network persistent=False
---------------------------------------------------------------------------------------
Play: container/ipmi_set_bootdev.yml
------------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/ipmi_set_bootdev.py {{ inventory }} {{ bootdev }} {{ persistent }} {{ log_level }}]


Include: container/ipmi_power_on.yml log_level=info
---------------------------------------------------
Play: container/ipmi_power_on.yml
---------------------------------
* Hosts: deployer

#. Power on all nodes \[command: {{ python_executable }} {{ scripts_path }}/python/ipmi_power_on.py {{ inventory }} {{ log_level }}]


Include: pause.yml minutes=5 message="Power-on Nodes"
-----------------------------------------------------
Play: Pause
-----------
* Hosts: localhost

#. Pause (seconds) \[pause]
#. Pause (minutes) \[pause]
#. Pause (wait for key press) \[pause]


Include: container/ipmi_set_bootdev.yml log_level=info bootdev=default persistent=True
--------------------------------------------------------------------------------------
Play: container/ipmi_set_bootdev.yml
------------------------------------
* Hosts: deployer

#. \[command: {{ python_executable }} {{ scripts_path }}/python/ipmi_set_bootdev.py {{ inventory }} {{ bootdev }} {{ persistent }} {{ log_level }}]


----

File: gather_mac_addresses.yml
==============================
Play: Clear switch MAC address table
------------------------------------
* Hosts: localhost

#. Include localhost variables #. Clear switch MAC address table switch and write them to the inventory file \[command: {{ python_executable_local }} {{ scripts_path_local }}/python/clear_port_macs.py /var/oprc/inventory.yml {{ log_level }}]

Play: Bring up all non-ansible comm interfaces on IPv6
------------------------------------------------------
* Hosts: all

#. Bring down all interfaces that are not the ansible communication interface \[command: ifdown {{ item }}]
#. Backup interfaces file \[command: cp /etc/network/interfaces /etc/network/interfaces.bak]
#. Write interfaces file for ipv6 auto on all interfaces \[template]
#. Bring up all interfaces \[command: ifup {{ item }}]

Play: Get MACs into the inventory file
--------------------------------------
* Hosts: localhost

#. Wait for interfaces to communicate with the switch \[pause]
#. Obtain interface MACs from the switch and write them to the inventory file \[command: {{ python_executable_local }} {{ scripts_path_local }}/python/set_port_macs.py /var/oprc/inventory.yml {{ log_level }}]

Play: Restore system interfaces
-------------------------------
* Hosts: all

#. Bring down all interfaces that are not the ansible communication interface \[command: ifdown {{ item }}]
#. Restore interfaces file \[command: cp /etc/network/interfaces.bak /etc/network/interfaces]
#. Bring up all interfaces \[command: ifup {{ item }}]

----

File: configure_operating_systems.yml
=====================================
Play: Gather facts from localhost
---------------------------------
* Hosts: localhost \[gather_facts: True]

Play: Configure interfaces
--------------------------
* Hosts: all

#. Unnamed task
    * Include: tasks/create_interfaces.yml
        #. Check for interface name collisions \[debug]
        #. Generate udev persistent net rules \[template]
        #. Generate interfaces file \[template]
        #. Reboot \[command: reboot]
        #. Wait for system to come back up
Play: Transfer keys
-------------------
* Hosts: controllers:compute

#. Unnamed task
    * Include: tasks/transfer_keys.yml
        #. Transferring private key \[copy]
        #. Transferring public key \[copy]

Play: Transfer inventory file
-----------------------------
* Hosts: controllers

#. Unnamed task
    * Include: tasks/transfer_inventory.yml
        #. Create inventory file target directory \[file]
        #. Transferring inventory file \[copy]

Play: Prepare Cluster Configuration Software
--------------------------------------------
* Hosts: controllers[0]

#. Unnamed task
    * Include: tasks/os_services_install.yml
        #. Debug \[debug]

