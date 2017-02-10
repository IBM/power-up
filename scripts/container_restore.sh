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

set -e
set -o pipefail

function usage {
    echo "usage: container_restore.sh container_archive [new_container_name]"
    exit $1
}

# Print usage info
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    usage 0
fi

# User must specify container backup filename
if [ -z "$1" ]; then
    echo "ERROR: Container archive filename must be specified!"
    echo
    usage 1
else
    FILENAME=$1
fi

if [ ! -f $FILENAME ]; then
    echo "ERROR: File not found!"
    echo
    usage 1
fi

# Extract original container name from config file
ORIGINALNAME=$(tar xzfO $FILENAME ./config | grep lxc.utsname | \
    awk '{print $3}')

# Optionally, user may specify new container name
if [ -z "$2" ]; then
    CONTAINERNAME=$ORIGINALNAME
else
    CONTAINERNAME=$2
fi

# Create container directory
sudo mkdir /var/lib/lxc/$CONTAINERNAME

# Unzip and untarcontainer files
sudo tar --numeric-owner -xzvf $FILENAME -C /var/lib/lxc/$CONTAINERNAME

if [ "$CONTAINERNAME" != "$ORIGINALNAME" ]; then
    sudo sed -i -- "s/$ORIGINALNAME/$CONTAINERNAME/g" \
        /var/lib/lxc/$CONTAINERNAME/config
fi

# Start container
sudo lxc-start -n $CONTAINERNAME

# Print completion message
echo "Container \"$FILENAME\" restored as \"$CONTAINERNAME\""

# Print LXC Info
sudo lxc-info -n $CONTAINERNAME
