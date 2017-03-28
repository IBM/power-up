Building the Introspection Kernel and Filesystem
================================================

Introspection enables the clients to boot a Linux mini-kernel and filesystem
prior to deployment. This allows Cluster Genesis to extract client hardware
resource information and provides an environment for users to run configuration
scripts (e.g. RAID volume management).

Building
--------------------

Introspection will need to be compiled on a ppc64le kernel/filesystem.

#.  Enter the introspection directory::

      cd introspection

#.  Execute setup.sh to download buildroot::

      ./setup.sh

#.  Generate buildroot and linux kernel config files (see below)
#.  Assign buildroot and kernel config files to environmental
    variables IS_BUILDROOT_CONFIG and IS_KERNEL_CONFIG respectively.
#.  Execute build.sh::

      ./build.sh

#.  Wait for buildroot to build needed packages, including the linux kernel.
#.  The final kernel and filesystem can be found under output/vmlinux and
    output/rootfs.cpio.gz respectively.
#.  If these two files are copied into
    'cluster-genesis/os_images/introspection' Cluster Genesis deploy will use
    them instead of calling the build scripts.

Building Necessary Config Files
-------------------------------
Until we are able to distribute our config files, we require that both the
kernel and buildroot config files be pointed to via environmental variables.

If you do not have premade config files, there are steps below on how to
create your own for use by the introspection build.

Buildroot Config Files
~~~~~~~~~~~~~~~~~~~~~~

After executing setup.sh enter the buildroot directory::

  cd buildroot

Execute make menuconfig::

  make menuconfig

In the menu, set the following options where each ---> is a submenu.
and any value in quotes("") requires the string be typed in by user::

  Target options ---> Target Architecture ---> PowerPC64 (little endian)

  Kernel ---> Linux Kernel

  Kernel Configuration ---> Using a custom (def) config file
  Kernel ---> Kernel binary format --> vmlinux

  Configuration file path ---> "kernel_config"
  System configuration ---> /dev management --> Dynamic using devtmpfs + eudev
  System configuration ---> Root filesystem overlay directories --> "overlayfs"

  Filesystem and flash utilities ---> cpio

  Interpreter languages and scripting ---> python
  Interpreter languages and scripting ---> python ---> core python modules ---> zlib module

  Target Packages ---> Firmware ---> linux-firmware
  Target Packages ---> Firmware ---> linux-firmware --> Ethernet firmware ---> Broadcom NetXtremeII

  Target Packages ---> Hardware handling ---> ipmitool
  Target Packages ---> Hardware handling ---> ipmitool ---> enable lanplus interface

  Target Packages ---> Network applications ---> dhcpcd
  Target Packages ---> Network applications ---> openssh

  Filesystem images ---> cpio the root filesystem (for use as an initial RAM filesystem)
  Filesystem images ---> cpio the root filesystem ---> Compression method (gzip)

Copy the resulting .config file to a location for future use::

  cp .config ../configs/buildroot_config

Assign IS_BUILDROOT_CONFIG to point to the new config file::

  cd ../
  export IS_BUILDROOT_CONFIG=configs/buildroot_config

Linux Kernel
~~~~~~~~~~~~~~~~~~~~~~

For the linux kernel, most of the config options we need(ppc64le architecture,
POWER8 etc) can be found in a default upstream config file named powernv_defconfig.


Download the defconfig::

  curl -o configs/powernv_defconfig 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/plain/arch/powerpc/configs/powernv_defconfig?h=v4.9&id=69973b830859bc6529a7a0468ba0d80ee5117826'

When the file is downloaded, there are two updates that need to applied to
powernv_defconfig in order to support additional network devices::

  CONFIG_BNX2X=y
  CONFIG_MLX4_EN=y

Once the file is modified, assign IS_KERNEL_CONFIG to point to the new kernel config file::

  export IS_KERNEL_CONFIG=configs/powernv_defconfig

Run Time
-------------------
Average load and build time on a POWER8 Server(~24 mins)

Public Keys
-------------------
To append a public key to the buildroot filesystem

#. Build.sh must have been run prior
#. Execute add_key.sh <key.pub>
#. The final updated filesystem will be placed into
   output/rootfs.cpio.gz



