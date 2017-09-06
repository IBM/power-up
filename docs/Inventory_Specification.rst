.. _inventory_file_spec:

Cluster Inventory File Specification
=====================================

**Specification Version: v2.0**

TODO: Short description of *inventory.yml* and how it should be used.

Each section represents a top level dictionary key:

| `version:`_
| `location:`_
| `switches:`_
| `nodes:`_

version:
--------

+-------------+------------------+--------------------------------------------------------------------------------------------------------------------------------------+----------+
| Element     | Example(s)       | Description                                                                                                                          | Required |
+=============+==================+======================================================================================================================================+==========+
|             |                  |                                                                                                                                      |          |
| ::          | ::               | Inventory file version.                                                                                                              | **yes**  |
|             |                  |                                                                                                                                      |          |
|   version:  |   version: v2.0  |  +----------------+----------------------------------+                                                                               |          |
|             |                  |  | Release Branch | Supported Inventory File Version |                                                                               |          |
|             |                  |  +================+==================================+                                                                               |          |
|             |                  |  | release-2.x    | version: v2.0                    |                                                                               |          |
|             |                  |  +----------------+----------------------------------+                                                                               |          |
|             |                  |  | release-1.x    | version: 1.0                     |                                                                               |          |
|             |                  |  +----------------+----------------------------------+                                                                               |          |
|             |                  |  | release-0.9    | version: 1.0                     |                                                                               |          |
|             |                  |  +----------------+----------------------------------+                                                                               |          |
|             |                  |                                                                                                                                      |          |
+-------------+------------------+--------------------------------------------------------------------------------------------------------------------------------------+----------+

location:
---------

See :ref:`Config Specification - Location Section <Config_Specification:location:>`.

switches:
---------

See :ref:`Config Specification - Switches Section <Config_Specification:switches:>`.

nodes:
------

::

  nodes:
      - label:
        hostname:
        rack_id:
        rack_eia:
        ipmi:
            switches:
            ports:
            userid:
            password:
        pxe:
            switches:
            ports:
            devices:
        data:
            switches:
            ports:
            devices:

+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
| Element              | Example(s)                    | Description                                                                                                    | Required |
+======================+===============================+================================================================================================================+==========+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | Type.                                                                                                          | **yes**  |
|                      |                               |                                                                                                                |          |
|   nodes:             |   label: ubuntu-servers       |                                                                                                                |          |
|       label:         |                               |                                                                                                                |          |
|       ...            |                               |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | Hostname.                                                                                                      | **yes**  |
|                      |                               |                                                                                                                |          |
|   nodes:             |   hostname: server-1          |                                                                                                                |          |
|       hostname:      |                               |                                                                                                                |          |
|       ...            |                               |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | Rack ID.                                                                                                       | no       |
|                      |                               |                                                                                                                |          |
|   nodes:             |   rack_id: rack_1             |                                                                                                                |          |
|       rack_id:       |                               |                                                                                                                |          |
|       ...            |                               |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | Rack EIA.                                                                                                      | no       |
|                      |                               |                                                                                                                |          |
|   nodes:             |   rack_eia: U10               |                                                                                                                |          |
|       rack_eia:      |                               |                                                                                                                |          |
|       ...            |                               |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | IPMI related parameters.                                                                                       | **yes**  |
|                      |                               |                                                                                                                |          |
|   nodes:             |   nodes:                      | | Required keys:                                                                                               |          |
|       ipmi:          |       ipmi:                   | |   *switches*  - Management switches.                                                                         |          |
|           switches:  |           switches:           | |   *ports*     - Management ports.                                                                            |          |
|           ports:     |           - mgmt_1            | |   *userid*    - IPMI userid.                                                                                 |          |
|           userid:    |           - mgmt_2            | |   *password*  - IPMI password.                                                                               |          |
|           password:  |           ports:              |                                                                                                                |          |
|       ...            |           - 1                 | List items are correlated by index.                                                                            |          |
|                      |           - 11                |                                                                                                                |          |
|                      |           userid: user        |                                                                                                                |          |
|                      |           password: passw0rd  |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | PXE related parameters.                                                                                        | **yes**  |
|                      |                               |                                                                                                                |          |
|   nodes:             |   nodes:                      | | Required keys:                                                                                               |          |
|       pxe:           |       pxe:                    | |   *switches*  - Management switches.                                                                         |          |
|           switches:  |           switches:           | |   *ports*     - Management ports.                                                                            |          |
|           ports:     |           - mgmt_1            | |   *devices*   - Network devices.                                                                             |          |
|           devices:   |           - mgmt_2            |                                                                                                                |          |
|       ...            |           ports:              | List items are correlated by index.                                                                            |          |
|                      |           - 2                 |                                                                                                                |          |
|                      |           - 12                |                                                                                                                |          |
|                      |           devices:            |                                                                                                                |          |
|                      |           - eth16             |                                                                                                                |          |
|                      |           - eth17             |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
|                      |                               |                                                                                                                |          |
| ::                   | ::                            | Data related parameters.                                                                                       | **yes**  |
|                      |                               |                                                                                                                |          |
|   nodes:             |   nodes:                      | | Required keys:                                                                                               |          |
|       data:          |       data:                   | |   *switches*  - Data switches.                                                                               |          |
|           switches:  |           switches:           | |   *ports*     - Data ports.                                                                                  |          |
|           ports:     |           - data_1            | |   *devices*   - Network devices.                                                                             |          |
|           devices:   |           - data_2            |                                                                                                                |          |
|       ...            |           ports:              | List items are correlated by index.                                                                            |          |
|                      |           - 1                 |                                                                                                                |          |
|                      |           - 2                 |                                                                                                                |          |
|                      |           devices:            |                                                                                                                |          |
|                      |           - eth26             |                                                                                                                |          |
|                      |           - eth27             |                                                                                                                |          |
|                      |                               |                                                                                                                |          |
+----------------------+-------------------------------+----------------------------------------------------------------------------------------------------------------+----------+
