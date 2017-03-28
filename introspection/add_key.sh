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
# Add  public key to target filesystems authorized_keys file
#
# 1) Takes a public key as input
# 2) Builds temp directory if not already done so.
# 3) Append new key to /root/.ssh/authorized_keys
# 4) Move new directories to existing overlayfs
# 5) Make last step of buildroot to add overlayfs
#
# Exit 0 on success; 1 on failure
#
set -e

PUBKEY_FILE=$1
INTROSPECTION_IMAGES=output
BUILDROOT_IMAGES=buildroot/output/images
OPWD=$(pwd)


#setup temporary directory
mkdir -p tmpdir/root/.ssh

#in case the file is nonexistant
touch tmpdir/root/.ssh/authorized_keys

#each run of add_key should add another key to the list
cat $PUBKEY_FILE >> tmpdir/root/.ssh/authorized_keys

#HACK but for now, we add our new dirs to the existing overlayfs.
cp -r tmpdir/* overlayfs/

#Run the last step of buildroot to overlay overlayfs and repackage
cd buildroot
make target-post-image

cd $OPWD

#Copy new rootfs images to introspection output
cp $BUILDROOT_IMAGES/* $INTROSPECTION_IMAGES/


