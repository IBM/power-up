#!/bin/bash
# Copyright 2017 IBM Corp.
#
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Build custom vmlinux and root filesystem for introspection
#
# 1) Clone buildroot from open-power
# 2) Move introspection configs into buildroot directory
# 3) Apply needed patches to buildroot(old ssh etc)
# 4) Execute buildroot makefile
# 5) Copy new kernel and root filesystem into introspection output dir
#
# Exit 0 on success; 1 on failure
#
set -e

IS_BUILDROOT_HOME=buildroot
IS_BUILDROOT_OUTPUT=output/images
IS_INTROSPECTION_OUTPUT=output

if [ "X$IS_BUILDROOT_CONFIG" = "X" ] ; then
    echo '$IS_BUILDROOT_CONFIG is not set.  Please specify buildroot config'
    exit 1
fi

if [ "X$IS_KERNEL_CONFIG" = "X" ] ; then
    echo '$IS_KERNEL_CONFIG is not set.  Please specify kernel config'
    exit 1
fi

cd $IS_BUILDROOT_HOME

#Move buildroot and kernel config files into buildroot dir.
cp $IS_BUILDROOT_CONFIG .config
cp $IS_KERNEL_CONFIG kernel_config

# build rootfs and kernel.
make

cd ../

#copy final rootfs and kernel to output directory
cp $IS_BUILDROOT_HOME/$IS_BUILDROOT_OUTPUT/rootfs.cpio.gz\
   $IS_INTROSPECTION_OUTPUT
cp $IS_BUILDROOT_HOME/$IS_BUILDROOT_OUTPUT/vmlinux\
   $IS_INTROSPECTION_OUTPUT
