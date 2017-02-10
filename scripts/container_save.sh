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
    echo "usage: container_save.sh [container_name]"
    exit $1
}

# Print usage info
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    usage 0
fi

# Set date
DATE=$(date +%Y-%m-%dT%H%M%z)

# Get hostname
HOST=$(hostname)

# Optionally, user may specify container name
if [[ -z "$1" ]]; then
    CONTAINERNAME="ubuntu-14-04-deployer"
else
    CONTAINERNAME=$1
fi

# Set container backup filename
FILENAME=$HOST.$DATE.$CONTAINERNAME.tgz

# Verify container exists
if ! sudo lxc-info -n $CONTAINERNAME; then
    echo
    usage 1
fi

# If running stop container
if sudo lxc-info -n $CONTAINERNAME -s | grep RUNNING; then
    echo "Stopping $CONTAINERNAME ..."
    sudo lxc-stop -n $CONTAINERNAME
    sudo lxc-info -n $CONTAINERNAME -s
fi

# Tar and gzip container files
sudo tar --numeric-owner -czvf $FILENAME -C /var/lib/lxc/$CONTAINERNAME ./

# Print completion message
echo "LXC container \"$CONTAINERNAME\" saved as \"$FILENAME\""
