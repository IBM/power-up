.. _config_file_spec:

Cluster Configuration File Specification
=========================================

**Specification Version: v2.0**

Genesis of the OpenPOWER Cloud Reference Cluster is controlled by the
'config.yml' file. This file is stored in YAML format. The definition of
the fields and the YAML file format are documented below.

Each section represents a top level dictionary key:

| `version:`_
| `location:`_
| `deployer:`_
| `switches:`_
| `interfaces:`_
| `networks:`_
| `node_templates:`_
| `software_bootstrap:`_

Additional key/value pairs are not processed by Cluster Genesis, but are
copied into the inventory.yml file and made available to post-Genesis
scripts and/or playbooks.


version:
---------

+-------------+------------------+--------------------------------------------------------------------------------------------------------------------------------------+----------+
| Element     | Example(s)       | Description                                                                                                                          | Required |
+=============+==================+======================================================================================================================================+==========+
|             |                  |                                                                                                                                      |          |
| ::          | ::               | Config file version.                                                                                                                 | **yes**  |
|             |                  |                                                                                                                                      |          |
|   version:  |   version: v2.0  |  +----------------+-------------------------------+                                                                                  |          |
|             |                  |  | Release Branch | Supported Config File Version |                                                                                  |          |
|             |                  |  +================+===============================+                                                                                  |          |
|             |                  |  | release-2.x    | version: v2.0                 |                                                                                  |          |
|             |                  |  +----------------+-------------------------------+                                                                                  |          |
|             |                  |  | release-1.x    | version: 1.1                  |                                                                                  |          |
|             |                  |  +----------------+-------------------------------+                                                                                  |          |
|             |                  |  | release-0.9    | version: 1.0                  |                                                                                  |          |
|             |                  |  +----------------+-------------------------------+                                                                                  |          |
|             |                  |                                                                                                                                      |          |
+-------------+------------------+--------------------------------------------------------------------------------------------------------------------------------------+----------+


location:
----------

::

  location:
      time_zone:
      data_center:
      racks:
          - label:
            room:
            row:
            cell:

+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
| Element              | Example(s)                    | Description                                                                                                    | Required |
+======================+===============================+================================================================================================================+==========+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | Cluster time zone in `tz database                                                                              | no       |
|                      |                               | <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_ format.                                       |          |
|   location:          |   time_zone: UTC              |                                                                                                                |          |
|       time_zone:     |                               |                                                                                                                |          |
|       ...            | ::                            |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
|                      |   time_zone: America/Chicago  |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | Data center name to be associated with cluster inventory.                                                      | no       |
|                      |                               |                                                                                                                |          |
|   location:          |   data_center: East Coast     |                                                                                                                |          |
|       data_center:   |                               |                                                                                                                |          |
|       ...            |                               |                                                                                                                |          |
|                      | ::                            |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
|                      |   data_center: Austin, TX     |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
| .. _location_racks:  |                               |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | List of cluster racks.                                                                                         | **yes**  |
|                      |                               |                                                                                                                |          |
|   location:          |   racks:                      | | Required keys:                                                                                               |          |
|       racks:         |       - label: rack1          | |   *label* - Unique label used to reference this rack elsewhere in the config file.                           |          |
|           - label:   |         room: lab41           |                                                                                                                |          |
|             room:    |         row: 5                | | Optional keys:                                                                                               |          |
|             row:     |         cell: B               | |   *room*  - Physical room location of rack.                                                                  |          |
|             cell:    |       - label: rack2          | |   *row*   - Physical row location of rack.                                                                   |          |
|       ...            |         room: lab41           | |   *cell*  - Physical cell location of rack.                                                                  |          |
|                      |         row: 5                |                                                                                                                |          |
|                      |         cell: C               |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+

deployer:
----------

::

  deployer:
      log_level:
      introspection:
      gateway:
      env_variables:
      networks:
          external:
              dev_label:
              dev_ipaddr:
              netmask:
          mgmt:
              container_ipaddr:
              bridge_ipaddr:
              netmask:
              vlan:
          client:
              container_ipaddr:
              bridge_ipaddr:
              netmask:
              vlan:

+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+
| Element                          | Example(s)                                 | Description                                                                                | Required |
+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+
|                                  |                                            |                                                                                            |          |
| ::                               | ::                                         | Minimum logger level to write to file. Options in order of decreasing verbosity:           | no       |
|                                  |                                            |                                                                                            |          |
|   deployer:                      |   log_level: debug                         |   | *debug*                                                                                |          |
|      log_level:                  |                                            |   | *info*                                                                                 |          |
|      ...                         | ::                                         |   | *warning*                                                                              |          |
|                                  |                                            |   | *error*                                                                                |          |
|                                  |   log_level: error                         |   | *critical*                                                                             |          |
|                                  |                                            |                                                                                            |          |
+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+
|                                  |                                            |                                                                                            |          |
| ::                               | ::                                         | Introspection shall be enabled. Evaluates to *false* if missing.                           | no       |
|                                  |                                            |                                                                                            |          |
|   deployer:                      |   introspection: true                      |   | *false*                                                                                |          |
|      introspection:              |                                            |   | *true*                                                                                 |          |
|      ...                         |                                            |                                                                                            |          |
|                                  |                                            |                                                                                            |          |
+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+
|                                  |                                            |                                                                                            |          |
| ::                               | ::                                         | Deployer shall act as cluster gateway. Evaluates to *false* if missing.                    | no       |
|                                  |                                            |                                                                                            |          |
|   deployer:                      |   gateway: true                            |   | *false*                                                                                |          |
|      gateway:                    |                                            |   | *true*                                                                                 |          |
|      ...                         |                                            |                                                                                            |          |
|                                  |                                            | The deployer will be configured as the default gateway for all client nodes.               |          |
|                                  |                                            |                                                                                            |          |
|                                  |                                            | Configuration includes adding a 'MASQUERADE' rule to the deployer's 'iptables' NAT chain   |          |
|                                  |                                            | and setting the 'dnsmasq' DHCP service to serve the deployer's client management bridge    |          |
|                                  |                                            | address as the default gateway.                                                            |          |
|                                  |                                            |                                                                                            |          |
|                                  |                                            | Note: Specifying the 'gateway' explicitly on any of the data networks will override this   |          |
|                                  |                                            | behaviour.                                                                                 |          |
|                                  |                                            |                                                                                            |          |
+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+
|                                  |                                            |                                                                                            |          |
| ::                               | ::                                         | Apply environmental variables to the shell.                                                | no       |
|                                  |                                            |                                                                                            |          |
|   deployer:                      |   env_variables:                           | The example to the left would give the following result in bash:                           |          |
|      env_variables:              |       https_proxy: http://192.168.1.2:3128 |                                                                                            |          |
|      ...                         |       http_proxy: http://192.168.1.2:3128  | | export https_proxy="http://192.168.1.2:3128"                                             |          |
|                                  |       no_proxy: localhost,127.0.0.1        | | export http_proxy="http://192.168.1.2:3128"                                              |          |
|                                  |                                            | | export no_proxy="localhost,127.0.0.1"                                                    |          |
|                                  |                                            |                                                                                            |          |
|                                  |                                            |                                                                                            |          |
+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+
|                                  |                                            |                                                                                            |          |
| ::                               | ::                                         | Deployer external network interface configuration. The external network is used to connect | **yes**  |
|                                  |                                            | to switch management ports on a network external to the Cluster Genesis environment.       |          |
|   deployer:                      |   external:                                |                                                                                            |          |
|       networks:                  |       dev_label: enp1s0f0                  | | Required keys:                                                                           |          |
|            external:             |       dev_ipaddr: 192.168.1.10             | |   *dev_label*  - Name of deployer's external interface                                   |          |
|                dev_label:        |       netmask: 255.255.255.0               | |   *dev_ipaddr* - IP address assigned to deployer's external interface.                   |          |
|                dev_ipaddr:       |                                            |                                                                                            |          |
|                netmask:          | ::                                         | | Subnet mask must be defined with *netmask* OR *prefix* (not both!):                      |          |
|            ...                   |                                            | |   *netmask* - External network bitmask.                                                  |          |
|       ...                        |    external:                               | |   *prefix*  - External network bit-length.                                               |          |
|                                  |        dev_label: enp1s0f0                 |                                                                                            |          |
|                                  |        dev_ipaddr: 192.168.1.10            |                                                                                            |          |
|                                  |        prefix: 24                          |                                                                                            |          |
|                                  |                                            |                                                                                            |          |
+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+
|                                  |                                            |                                                                                            |          |
| ::                               | ::                                         | Managment network configuration. The management network is used for swith management       | **yes**  |
|                                  |                                            | interfaces.                                                                                |          |
|   deployer:                      |   mgmt:                                    |                                                                                            |          |
|       networks:                  |       container_ipaddr: 192.168.5.2        | | Required keys:                                                                           |          |
|           mgmt:                  |       bridge_ipaddr: 192.168.5.3           | |   *container_ipaddr* - IP address assigned container management interface.               |          |
|               container_ipaddr:  |       netmask: 255.255.255.0               | |   *bridge_ipaddr*    - IP address assigned to deployer management bridge interface.      |          |
|               bridge_ipaddr:     |       vlan: 5                              | |   *vlan*             - Management network vlan.                                          |          |
|               netmask:           |                                            |                                                                                            |          |
|               vlan:              | ::                                         | | Subnet mask must be defined with *netmask* OR *prefix* (not both!):                      |          |
|           ...                    |                                            | |   *netmask* - Management network bitmask.                                                |          |
|       ...                        |   mgmt:                                    | |   *prefix*  - Management network bit-length.                                             |          |
|                                  |       container_ipaddr: 192.168.5.2        |                                                                                            |          |
|                                  |       bridge_ipaddr: 192.168.5.3           |                                                                                            |          |
|                                  |       prefix: 24                           |                                                                                            |          |
|                                  |       vlan: 5                              |                                                                                            |          |
|                                  |                                            |                                                                                            |          |
+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+
|                                  |                                            |                                                                                            |          |
| ::                               | ::                                         | Client network configuration. The client network is used for client node BMC (IPMI)        | **yes**  |
|                                  |                                            | and OS (PXE) interfaces. Ansible communicates with clients using this network during       |          |
|   deployer:                      |   client:                                  | "post deploy" operations.                                                                  |          |
|       networks:                  |       container_ipaddr: 192.168.20.2       |                                                                                            |          |
|           client:                |       bridge_ipaddr: 192.168.20.3          | | Required keys:                                                                           |          |
|               container_ipaddr:  |       netmask: 255.255.255.0               | |   *container_ipaddr* - IP address assigned container management interface.               |          |
|               bridge_ipaddr:     |       vlan: 20                             | |   *bridge_ipaddr*    - IP address assigned to deployer management bridge interface.      |          |
|               netmask:           |                                            | |   *vlan*             - Management network vlan.                                          |          |
|               vlan:              | ::                                         |                                                                                            |          |
|                                  |                                            | | Subnet mask must be defined with *netmask* OR *prefix* (not both!):                      |          |
|                                  |   client:                                  | |   *netmask* - Management network bitmask.                                                |          |
|                                  |       container_ipaddr: 192.168.20.2       | |   *prefix*  - Management network bit-length.                                             |          |
|                                  |       bridge_ipaddr: 192.168.20.3          |                                                                                            |          |
|                                  |       prefix: 24                           |                                                                                            |          |
|                                  |       vlan: 20                             |                                                                                            |          |
|                                  |                                            |                                                                                            |          |
+----------------------------------+--------------------------------------------+--------------------------------------------------------------------------------------------+----------+

switches:
----------

::

    switches:
        mgmt:
            - label:
              hostname:
              userid:
              password:
              ssh_key:
              rack_id:
              rack_eia:
              inband_interfaces:
                  - ipaddr:
                    port:
              external_links:
                  - target:
                    port:
        data:
            - label:
              hostname:
              userid:
              password:
              ssh_key:
              rack_id:
              rack_eia:
              external_links:
                  - target:
                    ipaddr:
                    vip:
                    port:

+---------------------------------+---------------------------------------+---------------------------------------------------------------------------------------------+----------+
| Element                         | Example(s)                            | Description                                                                                 | Required |
+=================================+=======================================+=============================================================================================+==========+
| .. _switches_mgmt:              |                                       |                                                                                             |          |
|                                 |                                       |                                                                                             |          |
| ::                              | ::                                    | Management switch configuration. Each physical switch is defined as an item in the *mgmt:*  | **yes**  |
|                                 |                                       | list.                                                                                       |          |
|   switches:                     |   mgmt:                               |                                                                                             |          |
|       mgmt:                     |       - label: mgmt_switch_1          | | Required keys:                                                                            |          |
|           - label:              |         userid: admin                 | |   *label*  - Unique label used to reference this switch elsewhere in the config file.     |          |
|             userid:             |         password: abc123              | |   *userid* [1]_ - Userid for switch management account.                                   |          |
|             password:           |         hostname: switch23423         |                                                                                             |          |
|             hostname:           |         rack_id: rack1                | | "Password" must [1]_ be defined with *password* OR *ssh_key* (not both!):                 |          |
|             rack_id:            |         rack_eia: 20                  | |   *password* - Plain text password associated with *userid*.                              |          |
|             rack_eia:           |         inband_interfaces:            | |   *ssh_key*  - Path to SSH private key file associated with *userid*.                     |          |
|             inband_interfaces:  |             - ipaddr: 192.168.1.20    |                                                                                             |          |
|                 - ipaddr:       |               port: 1                 | | Optional keys:                                                                            |          |
|                   port:         |         external_links:               | |   *hostname* - Hostname associated with switch management network interface.              |          |
|             external_links:     |             - target: deployer        | |   *rack_id*  - Reference to rack *label* defined in the `locations: racks:=               |          |
|                 - target:       |               port: 1                 |                  <location_racks_>`_ element.                                               |          |
|                   port:         |             - target: data_switch_1   | |   *rack_eia* - Switch position within rack.                                               |          |
|       ...                       |               port: 2                 | |   *inband_interfaces* - See inband_interfaces_.                                           |          |
|                                 |                                       | |   *external_links*    - See external_links_.                                              |          |
|                                 |                                       |                                                                                             |          |
|                                 |                                       | .. [1] *userid* and *password*/*ssh_key* are not required when running in passive switch    |          |
|                                 |                                       |    mode.                                                                                    |          |
|                                 |                                       |                                                                                             |          |
+---------------------------------+---------------------------------------+---------------------------------------------------------------------------------------------+----------+
| .. _switches_data:              |                                       |                                                                                             |          |
|                                 |                                       |                                                                                             |          |
| ::                              | ::                                    | Data switch configuration. Each physical switch is defined as an item in the *data:* list.  | **yes**  |
|                                 |                                       |                                                                                             |          |
|   switches:                     |   data:                               | Key/value specs are identical to `mgmt switches <switches_mgmt_>`_.                         |          |
|       data:                     |       - label: data_switch_1          |                                                                                             |          |
|           - label:              |         userid: admin                 |                                                                                             |          |
|             userid:             |         password: abc123              |                                                                                             |          |
|             password:           |         hostname: switch84579         |                                                                                             |          |
|             hostname:           |         rack_id: rack1                |                                                                                             |          |
|             rack_id:            |         rack_eia: 21                  |                                                                                             |          |
|             rack_eia:           |         inband_interfaces:            |                                                                                             |          |
|             inband_interfaces:  |             - ipaddr: 192.168.1.21    |                                                                                             |          |
|                 - ipaddr:       |               port: 1                 |                                                                                             |          |
|                   port:         |         external_links:               |                                                                                             |          |
|             external_links:     |             - target: deployer        |                                                                                             |          |
|                 - target:       |               port: 1                 |                                                                                             |          |
|                   port:         |             - target: data_switch     |                                                                                             |          |
|       ...                       |               port: 2                 |                                                                                             |          |
|                                 |                                       |                                                                                             |          |
+---------------------------------+---------------------------------------+---------------------------------------------------------------------------------------------+----------+
| .. _inband_interfaces:          |                                       |                                                                                             |          |
|                                 |                                       |                                                                                             |          |
| ::                              | ::                                    | Switch inband interface configuration.                                                      | no       |
|                                 |                                       |                                                                                             |          |
|   switches:                     |   inband_interfaces:                  |                                                                                             |          |
|       mgmt:                     |       - ipaddr: 192.168.1.20          | | Required keys:                                                                            |          |
|           - ...                 |         port: 1                       | |   *ipaddr* - IP address.                                                                  |          |
|             inband_interfaces:  |                                       | |   *port*   - Port number.                                                                 |          |
|                 - ipaddr:       |                                       |                                                                                             |          |
|                   port:         |                                       |                                                                                             |          |
|       data:                     |                                       |                                                                                             |          |
|           - ...                 |                                       |                                                                                             |          |
|             inband_interfaces:  |                                       |                                                                                             |          |
|                 - ipaddr:       |                                       |                                                                                             |          |
|                   port:         |                                       |                                                                                             |          |
|                                 |                                       |                                                                                             |          |
+---------------------------------+---------------------------------------+---------------------------------------------------------------------------------------------+----------+
| .. _external_links:             |                                       |                                                                                             |          |
|                                 |                                       |                                                                                             |          |
| ::                              | example #1::                          | Switch link configuration. Links can be configured between any switches and/or the          | no       |
|                                 |                                       | deployer.                                                                                   |          |
|   switches:                     |   mgmt:                               |                                                                                             |          |
|       mgmt:                     |       - label: mgmt_switch            | | Required keys:                                                                            |          |
|           - ...                 |         ...                           | |   *target* - Reference to destination target. This value must be set to 'deployer' or     |          |
|             external_links:     |         inband_interfaces:            |                correspond to another switch's *label* (switches_mgmt_, switches_data_).     |          |
|                 - target:       |             - ipaddr: 192.168.5.10    | |   *port*   - Source port number (not target port!). This can either be a single port or a |          |
|                   port:         |               port: 1                 |                list of ports. If a list is given then the links will be aggregated.         |          |
|       data:                     |         external_links:               |                                                                                             |          |
|           - ...                 |             - target: deployer        | | Optional keys:                                                                            |          |
|             external_links:     |               port: 10                | |   *ipaddr* - Management interface IP address.                                             |          |
|                 - target:       |             - target: data_switch     | |   *vlan*   - Management interface vlan                                                    |          |
|                   port:         |               port: 11                | |   *vip*    - Virtual IP used for redundant switch configurations.                         |          |
|           - ...                 |   data:                               |                                                                                             |          |
|             external_links:     |       - label: data_switch            | | Subnet mask may be defined with *netmask* OR *prefix* (not both!):                        |          |
|                 - target:       |         ...                           | |   *netmask* - Management network bitmask.                                                 |          |
|                   ipaddr:       |         external_links:               | |   *prefix*  - Management network bit-length.                                              |          |
|                   vip:          |             - target: mgmt_switch     |                                                                                             |          |
|                   netmask:      |               ipaddr: 192.168.5.11    | In example #1 port 10 of "mgmt_switch" is cabled directly to the deployer and port 11 of    |          |
|                   vlan:         |               vlan: 5                 | "mgmt_switch" is cabled to the mangement port 0 of "data_switch". An inband management      |          |
|                   port:         |               port: mgmt0             | interface is configured with an IP address of '192.168.5.10' for "mgmt_switch", and the     |          |
|                                 |                                       | dedicated management port 0 of "data_switch" is configured with an IP address of            |          |
|                                 | example #2::                          | "192.168.5.11" on vlan "5".                                                                 |          |
|                                 |                                       |                                                                                             |          |
|                                 |   data:                               | In example #2 a redundant data switch configuration is shown. Ports 7 and 8 (on both        |          |
|                                 |       - label: data_1_1               | switches) are configured as an aggrated peer link on vlan "4000" with IP address of         |          |
|                                 |         ...                           | "10.0.0.1/24" and "10.0.0.2/24".                                                            |          |
|                                 |         external_links:               |                                                                                             |          |
|                                 |             - target: mgmt_1          |                                                                                             |          |
|                                 |               ipaddr: 192.168.5.31    |                                                                                             |          |
|                                 |               vip: 192.168.5.254      |                                                                                             |          |
|                                 |               port: mgmt0             |                                                                                             |          |
|                                 |             - target: data_1_2        |                                                                                             |          |
|                                 |               ipaddr: 10.0.0.1        |                                                                                             |          |
|                                 |               netmask: 255.255.255.0  |                                                                                             |          |
|                                 |               vlan: 4000              |                                                                                             |          |
|                                 |               port:                   |                                                                                             |          |
|                                 |                   - 7                 |                                                                                             |          |
|                                 |                   - 8                 |                                                                                             |          |
|                                 |       - label: data_1_2               |                                                                                             |          |
|                                 |         external_links:               |                                                                                             |          |
|                                 |             - target: mgmt_1          |                                                                                             |          |
|                                 |               ipaddr: 192.168.5.31    |                                                                                             |          |
|                                 |               vip: 192.168.5.254      |                                                                                             |          |
|                                 |               port: mgmt0             |                                                                                             |          |
|                                 |             - target: data_1_1        |                                                                                             |          |
|                                 |               ipaddr: 10.0.0.2        |                                                                                             |          |
|                                 |               network: 255.255.255.0  |                                                                                             |          |
|                                 |               vlan: 4000              |                                                                                             |          |
|                                 |               port:                   |                                                                                             |          |
|                                 |                   - 7                 |                                                                                             |          |
|                                 |                   - 8                 |                                                                                             |          |
|                                 |                                       |                                                                                             |          |
+---------------------------------+---------------------------------------+---------------------------------------------------------------------------------------------+----------+


interfaces:
------------

::

    interfaces:
        - label:
          description:
          iface:
          method:
          address_list:
          netmask:
          broadcast:
          gateway:
          dns_search:
          dns_nameservers:
          mtu:
          pre_up:
          vlan_raw_device:
        - label:
          description:
          DEVICE:
          BOOTPROTO:
          IPADDR_list:
          NETMASK:
          BROADCAST:
          GATEWAY:
          SEARCH:
          DNS1:
          DNS2:
          MTU:
          VLAN:

+---------------------------+---------------------------------------------------+--------------------------------------------------------------------------------------------+----------+
| Element                   | Example(s)                                        | Description                                                                                | Required |
+===========================+===================================================+============================================================================================+==========+
|                           |                                                   |                                                                                            |          |
| ::                        |                                                   | List of OS interface configuration definitions. Each definition can be formatted for       | no       |
|                           |                                                   | either `Ubuntu <interfaces_ubuntu_>`_ or `RHEL <interfaces_rhel_>`_.                       |          |
|   interfaces:             |                                                   |                                                                                            |          |
|       - ...               |                                                   |                                                                                            |          |
|       - ...               |                                                   |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
+---------------------------+---------------------------------------------------+--------------------------------------------------------------------------------------------+----------+
| .. _interfaces_ubuntu:    |                                                   |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
| ::                        | ::                                                | Ubuntu formatted OS interface configuration.                                               | no       |
|                           |                                                   |                                                                                            |          |
|   interfaces:             |   - label: manual1                                | | Required keys:                                                                           |          |
|       - label:            |     description: manual network 1                 | |   *label*       - Unique label of interface configuration to be referenced within        |          |
|         description:      |     iface: eth0                                   |                     `networks:`_ `node_templates: interfaces:                              |          |
|         iface:            |     method: manual                                |                     <node_templates_interfaces_>`_.                                        |          |
|         method:           |                                                   |                                                                                            |          |
|         address_list:     |   - label: dhcp1                                  | | Optional keys:                                                                           |          |
|         netmask:          |     description: dhcp interface 1                 | |   *description*   - Short description of interface configuration to be included as a     |          |
|         broadcast:        |     iface: eth0                                   |                       comment in OS config files.                                          |          |
|         gateway:          |     method: dhcp                                  | |   *address_list*  - List of IP address to assign client interfaces referencing this      |          |
|         dns_search:       |                                                   |                       configuration. Each list element may either be a single IP address   |          |
|         dns_nameservers:  |   - label: static1                                |                       or a range (formatted as *<start_address>*-<*end_address*>).         |          |
|         mtu:              |     description: static interface 1               | |   *address_start* - Starting IP address to assign client interfaces referencing this     |          |
|         pre_up:           |     iface: eth0                                   |                       configuration. Addresses will be assigned to each client interface   |          |
|         vlan_raw_device:  |     method: static                                |                       incrementally.                                                       |          |
|                           |     address_list:                                 |                                                                                            |          |
|                           |         - 9.3.89.14                               | | Optional "drop-in" keys:                                                                 |          |
|                           |         - 9.3.89.18-9.3.89.22                     | |   The following key names are derived directly from the Ubuntu *interfaces*              |          |
|                           |         - 9.3.89.111-9.3.89.112                   |     configuration file (note that all "-" charactes are replaced with "_"). Values will be |          |
|                           |         - 9.3.89.120                              |     copied directly into the *interfaces* file. Refer to the `interfaces manpage           |          |
|                           |     netmask: 255.255.255.0                        |     <http://manpages.ubuntu.com/manpages/xenial/man5/interfaces.5.html>`_ for usage.       |          |
|                           |     broadcast: 9.3.89.255                         | |                                                                                          |          |
|                           |     gateway: 9.3.89.1                             | |   *iface*                                                                                |          |
|                           |     dns_search: your.dns.com                      | |   *method*                                                                               |          |
|                           |     dns_nameservers: 9.3.1.200 9.3.1.201          | |   *netmask*                                                                              |          |
|                           |     mtu: 9000                                     | |   *broadcast*                                                                            |          |
|                           |     pre_up: command                               | |   *gateway*                                                                              |          |
|                           |                                                   | |   *dns_search*                                                                           |          |
|                           |   - label: vlan1                                  | |   *dns_nameservers*                                                                      |          |
|                           |     description: vlan interface 1                 | |   *mtu*                                                                                  |          |
|                           |     iface: eth0.10                                | |   *pre_up*                                                                               |          |
|                           |     method: manual                                | |   *vlan_raw_device*                                                                      |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: vlan2                                  |                                                                                            |          |
|                           |     description: vlan interface 2                 |                                                                                            |          |
|                           |     iface: myvlan10                               |                                                                                            |          |
|                           |     method: manual                                |                                                                                            |          |
|                           |     vlan_raw_device: eth0                         |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bridge1                                |                                                                                            |          |
|                           |     description: bridge interface 1               |                                                                                            |          |
|                           |     iface: br1                                    |                                                                                            |          |
|                           |     method: static                                |                                                                                            |          |
|                           |     address_start: 10.0.0.100                     |                                                                                            |          |
|                           |     netmask: 255.255.255.0                        |                                                                                            |          |
|                           |     bridge_ports: eth0                            |                                                                                            |          |
|                           |     bridge_fd: 9                                  |                                                                                            |          |
|                           |     bridge_hello: 2                               |                                                                                            |          |
|                           |     bridge_maxage: 12                             |                                                                                            |          |
|                           |     bridge_stp: off                               |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bond1_interface0                       |                                                                                            |          |
|                           |     description: primary interface for bond 1     |                                                                                            |          |
|                           |     iface: eth0                                   |                                                                                            |          |
|                           |     method: manual                                |                                                                                            |          |
|                           |     bond_master: bond1                            |                                                                                            |          |
|                           |     bond_primary: eth0                            |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bond1_interface1                       |                                                                                            |          |
|                           |     description: secondary interface for bond 1   |                                                                                            |          |
|                           |     iface: eth1                                   |                                                                                            |          |
|                           |     method: manual                                |                                                                                            |          |
|                           |     bond_master: bond1                            |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bond1                                  |                                                                                            |          |
|                           |     description: bond interface 1                 |                                                                                            |          |
|                           |     iface: bond1                                  |                                                                                            |          |
|                           |     address_start: 192.168.1.10                   |                                                                                            |          |
|                           |     netmask: 255.255.255.0                        |                                                                                            |          |
|                           |     bond_mode: active-backup                      |                                                                                            |          |
|                           |     bond_miimon: 100                              |                                                                                            |          |
|                           |     bond_slaves: none                             |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: osbond0_interface0                     |                                                                                            |          |
|                           |     description: primary interface for osbond0    |                                                                                            |          |
|                           |     iface: eth0                                   |                                                                                            |          |
|                           |     method: manual                                |                                                                                            |          |
|                           |     bond_master: osbond0                          |                                                                                            |          |
|                           |     bond_primary: eth0                            |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: osbond0_interface1                     |                                                                                            |          |
|                           |     description: secondary interface for osbond0  |                                                                                            |          |
|                           |     iface: eth1                                   |                                                                                            |          |
|                           |     method: manual                                |                                                                                            |          |
|                           |     bond_master: osbond0                          |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: osbond0                                |                                                                                            |          |
|                           |     description: bond interface                   |                                                                                            |          |
|                           |     iface: osbond0                                |                                                                                            |          |
|                           |     address_start: 192.168.1.10                   |                                                                                            |          |
|                           |     netmask: 255.255.255.0                        |                                                                                            |          |
|                           |     bond_mode: active-backup                      |                                                                                            |          |
|                           |     bond_miimon: 100                              |                                                                                            |          |
|                           |     bond_slaves: none                             |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: osbond0_vlan10                         |                                                                                            |          |
|                           |     description: vlan interface 1                 |                                                                                            |          |
|                           |     iface: osbond0.10                             |                                                                                            |          |
|                           |     method: manual                                |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bridge10                               |                                                                                            |          |
|                           |     description: bridge interface for vlan10      |                                                                                            |          |
|                           |     iface: br10                                   |                                                                                            |          |
|                           |     method: static                                |                                                                                            |          |
|                           |     address_start: 10.0.10.100                    |                                                                                            |          |
|                           |     netmask: 255.255.255.0                        |                                                                                            |          |
|                           |     bridge_ports: osbond0.10                      |                                                                                            |          |
|                           |     bridge_stp: off                               |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: osbond0_vlan20                         |                                                                                            |          |
|                           |     description: vlan interface 2                 |                                                                                            |          |
|                           |     iface: osbond0.20                             |                                                                                            |          |
|                           |     method: manual                                |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bridge20                               |                                                                                            |          |
|                           |     description: bridge interface for vlan20      |                                                                                            |          |
|                           |     iface: br20                                   |                                                                                            |          |
|                           |     method: static                                |                                                                                            |          |
|                           |     address_start: 10.0.20.100                    |                                                                                            |          |
|                           |     netmask: 255.255.255.0                        |                                                                                            |          |
|                           |     bridge_ports: osbond0.20                      |                                                                                            |          |
|                           |     bridge_stp: off                               |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
+---------------------------+---------------------------------------------------+--------------------------------------------------------------------------------------------+----------+
| .. _interfaces_rhel:      |                                                   |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
| ::                        | ::                                                | RHEL styled OS interface configuration.                                                    | no       |
|                           |                                                   |                                                                                            |          |
|   interfaces:             |   - label: manual2                                | | Required keys:                                                                           |          |
|       - label:            |     description: manual network 2                 | |   *label*       - Unique label of interface configuration to be referenced within        |          |
|         description:      |     DEVICE: eth0                                  |                     `networks:`_ `node_templates: interfaces:                              |          |
|         DEVICE:           |     BOOTPROTO: none                               |                     <node_templates_interfaces_>`_.                                        |          |
|         BOOTPROTO:        |                                                   |                                                                                            |          |
|         IPADDR_list:      |   - label: dhcp2                                  | | Optional keys:                                                                           |          |
|         NETMASK:          |     description: dhcp interface 2                 | |   *description*  - Short description of interface configuration to be included as a      |          |
|         BROADCAST:        |     DEVICE: eth0                                  |                      comment in OS config files.                                           |          |
|         GATEWAY:          |     BOOTPROTO: dhcp                               | |   *IPADDR_list*  - List of IP address to assign client interfaces referencing this       |          |
|         SEARCH:           |                                                   |                      configuration. Each list element may either be a single IP address    |          |
|         DNS1:             |   - label: static2                                |                      or a range (formatted as *<start_address>*-<*end_address*>).          |          |
|         DNS2:             |     description: static interface 2               | |   *IPADDR_start* - Starting IP address to assign client interfaces referencing this      |          |
|         MTU:              |     DEVICE: eth0                                  |                      configuration. Addresses will be assigned to each client interface    |          |
|         VLAN:             |     BOOTPROTO: none                               |                      incrementally.                                                        |          |
|                           |     IPADDR_list:                                  |                                                                                            |          |
|                           |         - 9.3.89.14                               | | Optional "drop-in" keys:                                                                 |          |
|                           |         - 9.3.89.18-9.3.89.22                     | |   The following key names are derived directly from RHEL's *ifcfg* configuration files.  |          |
|                           |         - 9.3.89.111-9.3.89.112                   |     Values will be copied directly into the *ifcfg-<name>* files.  Refer to the `RHEL IP   |          |
|                           |         - 9.3.89.120                              |     NETWORKING <rhel_ifcfg_doc_>`_ for usage.                                              |          |
|                           |     NETMASK: 255.255.255.0                        | |                                                                                          |          |
|                           |     BROADCAST: 9.3.89.255                         | |   *DEVICE*                                                                               |          |
|                           |     GATEWAY: 9.3.89.1                             | |   *BOOTPROTO*                                                                            |          |
|                           |     SEARCH: your.dns.com                          | |   *NETMASK*                                                                              |          |
|                           |     DNS1: 9.3.1.200                               | |   *BROADCAST*                                                                            |          |
|                           |     DNS2: 9.3.1.201                               | |   *GATEWAY*                                                                              |          |
|                           |     MTU: 9000                                     | |   *SEARCH*                                                                               |          |
|                           |                                                   | |   *DNS1*                                                                                 |          |
|                           |   - label: vlan3                                  | |   *DNS2*                                                                                 |          |
|                           |     description: vlan interface 3                 | |   *MTU*                                                                                  |          |
|                           |     DEVICE: eth0.10                               | |   *VLAN*                                                                                 |          |
|                           |     BOOTPROTO: none                               |                                                                                            |          |
|                           |     VLAN: yes                                     |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bridge2                                |                                                                                            |          |
|                           |     description: bridge interface 2               |                                                                                            |          |
|                           |     DEVICE: br2                                   |                                                                                            |          |
|                           |     BOOTPROTO: static                             |                                                                                            |          |
|                           |     IPADDR_start: 10.0.0.100                      |                                                                                            |          |
|                           |     NETMASK: 255.255.255.0                        |                                                                                            |          |
|                           |     STP: off                                      |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bridge2_port                           |                                                                                            |          |
|                           |     description: port for bridge if 2             |                                                                                            |          |
|                           |     DEVICE: eth0                                  |                                                                                            |          |
|                           |     BOOTPROTO: none                               |                                                                                            |          |
|                           |     BRIDGE: br2                                   |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bond2_interface0                       |                                                                                            |          |
|                           |     description: primary interface for bond 2     |                                                                                            |          |
|                           |     DEVICE: eth0                                  |                                                                                            |          |
|                           |     BOOTPROTO: manual                             |                                                                                            |          |
|                           |     MASTER: bond2                                 |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bond2_interface1                       |                                                                                            |          |
|                           |     description: secondary interface for bond 2   |                                                                                            |          |
|                           |     DEVICE: eth1                                  |                                                                                            |          |
|                           |     BOOTPROTO: manual                             |                                                                                            |          |
|                           |     MASTER: bond2                                 |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
|                           |   - label: bond2                                  |                                                                                            |          |
|                           |     description: bond interface 2                 |                                                                                            |          |
|                           |     DEVICE: bond2                                 |                                                                                            |          |
|                           |     IPADDR_start: 192.168.1.10                    |                                                                                            |          |
|                           |     NETMASK: 255.255.255.0                        |                                                                                            |          |
|                           |     BONDING_OPTS: "mode=active-backup miimon=100" |                                                                                            |          |
|                           |                                                   |                                                                                            |          |
+---------------------------+---------------------------------------------------+--------------------------------------------------------------------------------------------+----------+

.. _rhel_ifcfg_doc: https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Networking_Guide/sec-Editing_Network_Configuration_Files.html#sec-Configuring_a_Network_Interface_Using_ifcg_Files

networks:
----------

::

    networks:
        - label:
          interfaces:

+----------------------+--------------------------+---------------------------------------------------------------------------------------------------------------------+----------+
| Element              | Example(s)               | Description                                                                                                         | Required |
+======================+==========================+=====================================================================================================================+==========+
|                      |                          |                                                                                                                     |          |
| ::                   | ::                       | The 'networks' list defines groups of interfaces. These groups can be assigned to items in the `node_templates:`_   | no       |
|                      |                          | list.                                                                                                               |          |
|   networks:          |   interfaces:            |                                                                                                                     |          |
|       - label:       |       - label: example1  | | Required keys:                                                                                                    |          |
|         interfaces:  |         ...              | |   *label*      - Unique label of network group to be referenced within a `node_templates:`_ item's 'networks:'    |          |
|                      |       - label: example2  |                    value.                                                                                           |          |
|                      |         ...              | |   *interfaces* - List of interfaces assigned to the group.                                                        |          |
|                      |       - label: example3  |                                                                                                                     |          |
|                      |         ...              |                                                                                                                     |          |
|                      |   networks:              |                                                                                                                     |          |
|                      |       - label: all_nets  |                                                                                                                     |          |
|                      |         interfaces:      |                                                                                                                     |          |
|                      |             - example1   |                                                                                                                     |          |
|                      |             - example2   |                                                                                                                     |          |
|                      |             - example3   |                                                                                                                     |          |
|                      |       - label: group1    |                                                                                                                     |          |
|                      |         interfaces:      |                                                                                                                     |          |
|                      |             - example1   |                                                                                                                     |          |
|                      |             - example2   |                                                                                                                     |          |
|                      |       - label: group2    |                                                                                                                     |          |
|                      |         interfaces:      |                                                                                                                     |          |
|                      |             - example1   |                                                                                                                     |          |
|                      |             - example3   |                                                                                                                     |          |
|                      |                          |                                                                                                                     |          |
+----------------------+--------------------------+---------------------------------------------------------------------------------------------------------------------+----------+


node_templates:
----------------

::

    node_templates:
        - label:
          ipmi:
              userid:
              password:
          os:
              hostname_prefix:
              profile:
              install_device:
              users:
                  - name:
                    password:
              groups:
                  - name:
          physical_interfaces:
              ipmi:
                  - switch:
                    ports:
              pxe:
                  - switch:
                    dev:
                    rename:
                    ports:
              data:
                  - switch:
                    dev:
                    rename:
                    ports:
          interfaces:
          networks:
          roles:

+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| Element                            | Example(s)                                    | Description                                                                      | Required |
+====================================+===============================================+==================================================================================+==========+
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | Node templates define client node configurations. Existing IPMI credentials and  | **yes**  |
|                                    |                                               | network interface physical connection information must be given to allow Cluster |          |
|   node_templates:                  |   - label: controllers                        | Genesis to connect to nodes. OS installation characteristics and post install    |          |
|       - label:                     |     ipmi:                                     | network configurations are also defined.                                         |          |
|         ipmi:                      |         userid: admin                         |                                                                                  |          |
|         os:                        |         password: pass                        | | Required keys:                                                                 |          |
|         physical_interfaces:       |     os:                                       | |   *label*   - Unique label used to reference this template.                    |          |
|         interfaces:                |         hostname_prefix: ctrl                 | |   *ipmi*    - IPMI credentials. See `node_templates: ipmi                      |          |
|         networks:                  |         profile: ubuntu-14.04-server-ppc64el  |                 <node_templates_ipmi_>`_.                                        |          |
|         roles:                     |         install_device: /dev/sda              | |   *os*      - Operating system configuration. See `node_templates: os          |          |
|                                    |     physical_interfaces:                      |                 <node_templates_os_>`_.                                          |          |
|                                    |         ipmi:                                 | |   *physical_interfaces* - Physical network interface port mappings. See        |          |
|                                    |             - switch: mgmt_switch_1           |                             `node_templates: physical_interfaces                 |          |
|                                    |               ports:                          |                             <node_templates_physical_ints_>`_.                   |          |
|                                    |                   - 1                         |                                                                                  |          |
|                                    |                   - 3                         | | Optional keys:                                                                 |          |
|                                    |                   - 5                         | |   *interfaces* - Post-deploy interface assignments. See `node_templates:       |          |
|                                    |         pxe:                                  |                    interfaces <node_templates_interfaces_>`_.                    |          |
|                                    |             - switch: mgmt_switch_1           | |   *networks*   - Post-deploy network (interface group) assignments. See        |          |
|                                    |               ports:                          |                    `node_templates: networks <node_templates_networks_>`_.       |          |
|                                    |                   - 2                         | |   *roles*      - Ansible group assignment. See `node_templates: roles          |          |
|                                    |                   - 4                         |                    <node_templates_roles_>`_.                                    |          |
|                                    |                   - 6                         |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| .. _node_templates_ipmi:           |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | Client node IPMI credentials. Note that IPMI credentials must be consistent for  | **yes**  |
|                                    |                                               | all members of a node template.                                                  |          |
|   node_templates:                  |   - label: ppc64el                            |                                                                                  |          |
|       - ...                        |     ipmi:                                     | | Required keys:                                                                 |          |
|         ipmi:                      |         userid: ADMIN                         | |   *userid*   - IPMI userid.                                                    |          |
|             userid:                |         password: admin                       | |   *password* - IPMI password.                                                  |          |
|             password:              |     ...                                       |                                                                                  |          |
|                                    |   - lable: x86_64                             |                                                                                  |          |
|                                    |     ipmi:                                     |                                                                                  |          |
|                                    |         userid: ADMIN                         |                                                                                  |          |
|                                    |         password: ADMIN                       |                                                                                  |          |
|                                    |     ...                                       |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| .. _node_templates_os:             |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | Client node operating system configuration.                                      | **yes**  |
|                                    |                                               |                                                                                  |          |
|   node_templates:                  |   - ...                                       | | Required keys:                                                                 |          |
|       - ...                        |     os:                                       |                                                                                  |          |
|         os:                        |         hostname_prefix: controller           |                                                                                  |          |
|             hostname_prefix:       |         profile: ubuntu-14.04-server-ppc64el  |                                                                                  |          |
|             profile:               |         install_device: /dev/sda              |                                                                                  |          |
|             install_device:        |         users:                                | |   *profile*         - Cobbler profile to use for OS installation. This name    |          |
|             users:                 |             - name: root                      |                         usually should match the name of the installation image  |          |
|                 - name:            |               password: passw0rd              |                         (without the'.iso' extension).                           |          |
|                   password:        |             - name: user1                     | |   *install_device*  - Path to installation disk device.                        |          |
|             groups:                |               password: abc123                |                                                                                  |          |
|                 - name:            |               groups: sudo,testgroup1         | | Optional keys:                                                                 |          |
|                                    |         groups:                               | |   *hostname_prefix* - Prefix used to assign hostnames to client nodes          |          |
|                                    |             - name: testgroup1                |                         belonging to this node template. A "-" and enumeration   |          |
|                                    |             - name: testgroup2                |                         is added to the end of the prefix to make a unique       |          |
|                                    |                                               |                         hostname for each client node (e.g. "controller-1" and   |          |
|                                    |                                               |                         "controoler-2").                                         |          |
|                                    |                                               | |   *users*           - OS user accounts to create. All parameters in the        |          |
|                                    |                                               |                         `Ansible user module <ansible_user_module_>`_ are        |          |
|                                    |                                               |                         supported.                                               |          |
|                                    |                                               | |   *groups*          - OS groups to create. All parameters in the `Ansible      |          |
|                                    |                                               |                         group module <ansible_group_module_>`_ are supported.    |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| .. _node_templates_physical_ints:  |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | Client node operating system configuration.                                      | **yes**  |
|                                    |                                               |                                                                                  |          |
|   node_templates:                  |   - ...                                       | | Required keys:                                                                 |          |
|       - ...                        |     physical_interfaces:                      | |   *ipmi* - IPMI (BMC) interface port mappings. See `physical_interfaces: ipmi  |          |
|         physical_interfaces:       |         ipmi:                                 |              <physical_ints_ipmi_>`_.                                            |          |
|             ipmi:                  |             - switch: mgmt_1                  | |   *pxe*  - PXE (OS) interface port mappings. See `physical_interfaces:         |          |
|                 - switch:          |               ports:                          |              pxe/data <physical_ints_os_>`_.                                     |          |
|                   ports:           |                   - 7                         |                                                                                  |          |
|             pxe:                   |                   - 8                         | | Optional keys:                                                                 |          |
|                 - switch:          |                   - 9                         | |   *data* - Data (OS) interface port mappings. See `physical_interfaces:        |          |
|                   dev:             |         pxe:                                  |              pxe/data <physical_ints_os_>`_.                                     |          |
|                   rename:          |             - switch: mgmt_1                  |                                                                                  |          |
|                   ports:           |               dev: eth15                      |                                                                                  |          |
|             data:                  |               rename: true                    |                                                                                  |          |
|                 - switch:          |               ports:                          |                                                                                  |          |
|                   dev:             |                   - 10                        |                                                                                  |          |
|                   rename:          |                   - 11                        |                                                                                  |          |
|                   ports:           |                   - 12                        |                                                                                  |          |
|                                    |         data:                                 |                                                                                  |          |
|                                    |             - switch: data_1                  |                                                                                  |          |
|                                    |               dev: eth10                      |                                                                                  |          |
|                                    |               rename: true                    |                                                                                  |          |
|                                    |               ports:                          |                                                                                  |          |
|                                    |                   - 7                         |                                                                                  |          |
|                                    |                   - 8                         |                                                                                  |          |
|                                    |                   - 9                         |                                                                                  |          |
|                                    |             - switch: data_1                  |                                                                                  |          |
|                                    |               dev: eth11                      |                                                                                  |          |
|                                    |               rename: false                   |                                                                                  |          |
|                                    |               ports:                          |                                                                                  |          |
|                                    |                   - 10                        |                                                                                  |          |
|                                    |                   - 11                        |                                                                                  |          |
|                                    |                   - 12                        |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| .. _physical_ints_ipmi:            |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | IPMI (BMC) interface port mappings.                                              | **yes**  |
|                                    |                                               |                                                                                  |          |
|   node_templates:                  |   - ...                                       | | Required keys:                                                                 |          |
|       - ...                        |     physical_interfaces:                      | |   *switch* - Reference to mgmt switch *label* defined in the `switches: mgmt:  |          |
|         physical_interfaces:       |         ipmi:                                 |                <switches_mgmt_>`_ element.                                       |          |
|             ipmi:                  |             - switch: mgmt_1                  | |   *ports*  - List of port number/identifiers mapping to client node IPMI       |          |
|                 - switch:          |               ports:                          |                interfaces.                                                       |          |
|                   ports:           |                   - 7                         |                                                                                  |          |
|             ...                    |                   - 8                         | In the example three client nodes are defined and mapped to ports 7,8,9 of a     |          |
|                                    |                   - 9                         | management switch labeled "mgmt_1".                                              |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| .. _physical_ints_os:              |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | OS (PXE & data) interface port mappings.                                         | **yes**  |
|                                    |                                               |                                                                                  |          |
|   node_templates:                  |   - ...                                       | | Required keys:                                                                 |          |
|       - ...                        |     physical_interfaces:                      | |   *switch* - Reference to switch *label* defined in the `switches: mgmt:       |          |
|         physical_interfaces:       |         pxe:                                  |                <switches_mgmt_>`_ or `switches: data: <switches_data_>`_         |          |
|             ...                    |             - switch: mgmt_1                  |                elements.                                                         |          |
|             pxe:                   |               dev: eth15                      | |   *dev*    - Reference to interface label defined in the `interfaces:`_        |          |
|                 - switch:          |               rename: true                    |                elements.                                                         |          |
|                   dev:             |               ports:                          | |   *rename* - Value (true/false) to control whether client node interfaces will |          |
|                   rename:          |                   - 10                        |                be renamed to match the 'dev' value.                              |          |
|                   ports:           |                   - 11                        | |   *ports*  - List of port number/identifiers mapping to client node OS         |          |
|             data:                  |                   - 12                        |                interfaces.                                                       |          |
|                 - siwtch:          |         data:                                 |                                                                                  |          |
|                   dev:             |             - switch: data_1                  |                                                                                  |          |
|                   rename:          |               dev: eth10                      |                                                                                  |          |
|                   ports            |               rename: true                    |                                                                                  |          |
|                                    |               ports:                          |                                                                                  |          |
|                                    |                   - 7                         |                                                                                  |          |
|                                    |                   - 8                         |                                                                                  |          |
|                                    |                   - 9                         |                                                                                  |          |
|                                    |             - switch: data_1                  |                                                                                  |          |
|                                    |               dev: eth11                      |                                                                                  |          |
|                                    |               rename: false                   |                                                                                  |          |
|                                    |               ports:                          |                                                                                  |          |
|                                    |                   - 10                        |                                                                                  |          |
|                                    |                   - 11                        |                                                                                  |          |
|                                    |                   - 12                        |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| .. _node_templates_interfaces:     |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | OS network interface configuration assignment.                                   | no       |
|                                    |                                               |                                                                                  |          |
|   node_templates:                  |   interfaces:                                 | | Required keys:                                                                 |          |
|       - ...                        |       - label: data_int1                      | |   *interfaces* - List of references to interface *labels* from the top-level   |          |
|         interfaces:                |       ...                                     |                    `interfaces:`_ dictionary.                                    |          |
|                                    |       - label: data_int2                      |                                                                                  |          |
|                                    |       ...                                     |                                                                                  |          |
|                                    |       - label: data_int3                      |                                                                                  |          |
|                                    |       ...                                     |                                                                                  |          |
|                                    |   node_templates:                             |                                                                                  |          |
|                                    |       - ...                                   |                                                                                  |          |
|                                    |         interfaces:                           |                                                                                  |          |
|                                    |             - data_int1                       |                                                                                  |          |
|                                    |             - data_int2                       |                                                                                  |          |
|                                    |             - data_int3                       |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| .. _node_templates_networks:       |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | OS network interface configuration assignment by group.                          | no       |
|                                    |                                               |                                                                                  |          |
|   node_templates:                  |   interfaces:                                 | | Required keys:                                                                 |          |
|       - ...                        |       - label: data_int1                      | |   *networks* - List of references to network *labels* from the top-level       |          |
|         networks:                  |       ...                                     |                  `networks:`_ dictionary.                                        |          |
|                                    |       - label: data_int2                      |                                                                                  |          |
|                                    |       ...                                     |                                                                                  |          |
|                                    |       - label: data_int3                      |                                                                                  |          |
|                                    |       ...                                     |                                                                                  |          |
|                                    |   networks:                                   |                                                                                  |          |
|                                    |       - label: data_group1                    |                                                                                  |          |
|                                    |         interfaces:                           |                                                                                  |          |
|                                    |             - data_int1                       |                                                                                  |          |
|                                    |             - data_int2                       |                                                                                  |          |
|                                    |             - data_int3                       |                                                                                  |          |
|                                    |   node_templates:                             |                                                                                  |          |
|                                    |       - ...                                   |                                                                                  |          |
|                                    |         networks:                             |                                                                                  |          |
|                                    |             - data_group1                     |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+
| .. _node_templates_roles:          |                                               |                                                                                  |          |
|                                    |                                               |                                                                                  |          |
| ::                                 | ::                                            | Ansible role/group assignment.                                                   | no       |
|                                    |                                               |                                                                                  |          |
|   node_templates:                  |   roles:                                      | | Required keys:                                                                 |          |
|       - ...                        |       - controllers                           | |   *roles* - List of roles (Ansible groups) to assign to client nodes           |          |
|         roles:                     |       - power_servers                         |               associated with this node template. Names can be any string.       |          |
|                                    |                                               |                                                                                  |          |
+------------------------------------+-----------------------------------------------+----------------------------------------------------------------------------------+----------+

.. _ansible_user_module: http://docs.ansible.com/ansible/latest/user_module.html
.. _ansible_group_module: http://docs.ansible.com/ansible/latest/group_module.html


software_bootstrap:
--------------------

::

    software_bootstrap:
        - hosts:
          executable:
          command:

+-------------------------+----------------------------------+----------------------------------------------------------------------------------------------------------+----------+
| Element                 | Example(s)                       | Description                                                                                              | Required |
+=========================+==================================+==========================================================================================================+==========+
|                         |                                  |                                                                                                          |          |
| ::                      | ::                               | Software bootstrap defines commands to be run on client nodes after Cluster Genesis completes. This is   | no       |
|                         |                                  | useful for various additional configuration activities, such as bootstrapping additional software        |          |
|   software_bootstrap:   |   software_bootstrap:            | package installations.                                                                                   |          |
|       - hosts:          |       - hosts: all               |                                                                                                          |          |
|         executable:     |         command: apt-get update  | | Required keys:                                                                                         |          |
|         command:        |       - hosts: openstackservers  | |   *hosts*   - Hosts to run commands on. The value can be set to 'all' to run on all hosts,             |          |
|                         |         executable: /bin/bash    |                 node_template labels, or role/group names.                                               |          |
|                         |         command: |               | |   *command* - Command to run.                                                                          |          |
|                         |           set -e                 |                                                                                                          |          |
|                         |           apt update             | | Optional keys:                                                                                         |          |
|                         |           apt upgrade -y         | |   *executable* - Path to shell used to execute the command.                                            |          |
|                         |                                  |                                                                                                          |          |
+-------------------------+----------------------------------+----------------------------------------------------------------------------------------------------------+----------+
