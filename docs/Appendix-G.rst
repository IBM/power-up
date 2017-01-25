
Appendix - G Configuring Management Access on the Lenovo G8052 and Mellanox SX1410
==================================================================================

For the Lenovo G8052 switch, the following commands can be used to
configure management access on interface 1.

-  G8052> enable
-  G8052 # configure terminal
-  (config) # interface ip 1
-  (config-ip-if) # ip address 192.168.16.5 (example ipv4 address)
-  (config-ip-if) # ip netmask 255.255.255.0 (example netmask)
-  (config-ip-if) # vlan 1
-  (config-ip-if) # enable
-  (config-ip-if) # exit

Note: if you are SSH'd into the switch on interface 1, be careful not to
cut off access if changing the ip address. If needed, additional
management interfaces can be set up on interfaces 2, 3 or 4.

For the Mellanox switch, the following commands can be used to configure
the MGMT0 management port;

switch (config) # no interface mgmt0 dhcp

switch (config) # interface mgmt0 ip address <IP address> <netmask>

For the Mellanox switch, the following commands can be used to configure
an in-band management interface on an existing vlan ; (example vlan 10)

switch (config) # interface vlan 10

switch (config interface vlan 10) # ip address 10.10.10.10 /24

To check the config;

switch (config) # show interfaces vlan 10
