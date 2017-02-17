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

# Set date
DATE=$(date +%Y-%m-%dT%H%M%z)

# Get hostname
HOST=$(hostname)

# Get cluster-genesis top level directory
PROJECT_DIR=$(git rev-parse --show-toplevel)

PLAYBOOKS="${PROJECT_DIR}/playbooks"

# Get container SSH connection info from ansible hosts file
SSH_USER=$(grep -oh "ansible_user=[^ ]*" "${PLAYBOOKS}/hosts" | \
    awk -F = '{print $2}')
SSH_HOST=$(grep -oh "ansible_host=[^ ]*" "${PLAYBOOKS}/hosts" | \
    awk -F = '{print $2}')
SSH_KEY=$(grep -oh "ansible_ssh_private_key_file=[^ ]*" \
    "${PLAYBOOKS}/hosts" | awk -F = '{print $2}')

# Create Directories
TAG="logdump.$HOST.$DATE"
if [ ! -d "${PROJECT_DIR}/debug_data" ]; then
    mkdir "${PROJECT_DIR}/debug_data"
fi
LOGS_DIR="${PROJECT_DIR}/debug_data/${TAG}"
mkdir $LOGS_DIR

# Local Deployer File Pointers
DEPLOYER_INFO_SAVE="${LOGS_DIR}/${TAG}.deployer.info.txt"

GIT_REPO_INFO_SAVE="${LOGS_DIR}/${TAG}.deployer.git_diff_head.txt"

CONFIG_PATH="${PROJECT_DIR}/config.yml"
CONFIG_SAVE="${LOGS_DIR}/${TAG}.deployer.config.yml"

CONFIG_BACKUP_PATH="${PROJECT_DIR}/config-backup.yml"
CONFIG_BACKUP_SAVE="${LOGS_DIR}/${TAG}.deployer.config-backup.yml"

INV_DEPLOYER_PATH="/var/oprc/inventory.yml"
INV_DEPLOYER_SAVE="${LOGS_DIR}/${TAG}.deployer.inventory.yml"

ANSIBLE_LOG_PATH="${PLAYBOOKS}/ansible.log"
ANSIBLE_LOG_SAVE="${LOGS_DIR}/${TAG}.deployer.ansible.log"

LXC_CONF_PATH="${PLAYBOOKS}/lxc.conf"
LXC_CONF_SAVE="${LOGS_DIR}/${TAG}.deployer.lxc.conf"

# Container File Pointers
INV_CONTAINER_PATH="~/cluster-genesis/inventory.yml"
INV_CONTAINER_SAVE="${LOGS_DIR}/${TAG}.container.inventory.yml"

GENESIS_LOG_PATH="~/cluster-genesis/log.txt"
GENESIS_LOG_SAVE="${LOGS_DIR}/${TAG}.container.log.txt"

# Functions to save files
save_local_file ()
{
    if [ -f $1 ]; then
        echo "Saving $1 to $2"
        cp -p $1 $2
    else
        echo "File not found!: $1"
    fi
}

ssh_cmd ()
{
    ssh -i $SSH_KEY $SSH_USER@$SSH_HOST $1
}

save_container_file ()
{
    if ssh_cmd "[ -f $1 ]"; then
        echo "Saving $SSH_HOST:$1 to $2"
        scp -p -i $SSH_KEY $SSH_USER@$SSH_HOST:$1 $2
    else
        echo "Container File not found!: $SSH_HOST:$1"
    fi
}

collect_deployer_access_info ()
{
    read -p "Deployer Hostname/IP: " host
    read -p "Deployer User: " user
    read -p "Deployer Password: " pass
    read -p "Additional Notes: " notes
}

display_deployer_access_info ()
{
    echo "Deployer Hostname/IP: $host"
    echo "Deployer User: $user"
    echo "Deployer Password: $pass"
    echo "Additional Notes: $notes"
}

save_deployer_access_info ()
{
    echo "## Deployer Access Information #########" >> $DEPLOYER_INFO_SAVE
    echo "Deployer Hostname/IP: $host" >> $DEPLOYER_INFO_SAVE
    echo "Deployer User: $user" >> $DEPLOYER_INFO_SAVE
    echo "Deployer Password: $pass" >> $DEPLOYER_INFO_SAVE
    echo "Additional Notes: $notes" >> $DEPLOYER_INFO_SAVE
    echo >> $DEPLOYER_INFO_SAVE
}

prompt_deployer_access_info ()
{

    while true; do
        collect_deployer_access_info
        echo
        echo "Please confirm the information above is correct"
        echo
        read -p "[yes/no]: " yn
        case $yn in
            [Yy]* ) save_deployer_access_info; break;;
            [Nn]* ) ;;
            * ) echo "Please answer yes or no.";;
        esac
    done

}


# Collect Data!
echo "Saving deployer information to $DEPLOYER_INFO_SAVE"
echo "############################" > $DEPLOYER_INFO_SAVE
date >> $DEPLOYER_INFO_SAVE
echo "############################" >> $DEPLOYER_INFO_SAVE
echo >> $DEPLOYER_INFO_SAVE

while true; do
    read -p "Do you wish to include deployer access information? [yes/no]: " yn
    case $yn in
        [Yy]* ) prompt_deployer_access_info; break;;
        [Nn]* ) break;;
        * ) echo "Please answer yes or no.";;
    esac
done

echo "## Deployer OS Information #############" >> $DEPLOYER_INFO_SAVE
hostname >> $DEPLOYER_INFO_SAVE
cat /etc/os-release >> $DEPLOYER_INFO_SAVE
uname -a >> $DEPLOYER_INFO_SAVE
echo >> $DEPLOYER_INFO_SAVE

echo "## User and Working Directory ##########" >> $DEPLOYER_INFO_SAVE
whoami >> $DEPLOYER_INFO_SAVE
pwd >> $DEPLOYER_INFO_SAVE
echo >> $DEPLOYER_INFO_SAVE

echo "## Project Repository Information ######" >> $DEPLOYER_INFO_SAVE
git show -s HEAD >> $DEPLOYER_INFO_SAVE
git status >> $DEPLOYER_INFO_SAVE
git log --oneline >> $DEPLOYER_INFO_SAVE
echo >> $DEPLOYER_INFO_SAVE

echo "[sudo required to collect lxc status]"
echo "## Deployer LXC Information ############" >> $DEPLOYER_INFO_SAVE
sudo lxc-ls -f >> $DEPLOYER_INFO_SAVE
echo >> $DEPLOYER_INFO_SAVE

echo "## Deployer Network Configuration ######" >> $DEPLOYER_INFO_SAVE
ip addr >> $DEPLOYER_INFO_SAVE

echo "Saving git diff to $GIT_REPO_INFO_SAVE"
echo "############################" > $GIT_REPO_INFO_SAVE
date >> $GIT_REPO_INFO_SAVE
echo "############################" >> $GIT_REPO_INFO_SAVE
echo >> $GIT_REPO_INFO_SAVE

echo "## git show -s HEAD ####################" >> $GIT_REPO_INFO_SAVE
git show -s HEAD >> $GIT_REPO_INFO_SAVE
echo >> $GIT_REPO_INFO_SAVE

echo "## git status ##########################" >> $GIT_REPO_INFO_SAVE
git status >> $GIT_REPO_INFO_SAVE
echo >> $GIT_REPO_INFO_SAVE

echo "## git log --oneline ###################" >> $GIT_REPO_INFO_SAVE
git log --oneline >> $GIT_REPO_INFO_SAVE
echo >> $GIT_REPO_INFO_SAVE

echo "## git diff HEAD #######################" >> $GIT_REPO_INFO_SAVE
git diff HEAD >> $GIT_REPO_INFO_SAVE
echo >> $GIT_REPO_INFO_SAVE


# Save off local deployer files
save_local_file $CONFIG_PATH $CONFIG_SAVE
save_local_file $CONFIG_BACKUP_PATH $CONFIG_BACKUP_SAVE
save_local_file $INV_DEPLOYER_PATH $INV_DEPLOYER_SAVE
save_local_file $ANSIBLE_LOG_PATH $ANSIBLE_LOG_SAVE
save_local_file $LXC_CONF_PATH $LXC_CONF_SAVE

# Save off files in container
save_container_file "~/fake.file" "filler"
save_container_file $INV_CONTAINER_PATH $INV_CONTAINER_SAVE
save_container_file $GENESIS_LOG_PATH $GENESIS_LOG_SAVE

# Tar & compress logs
tar -cvzf "${LOGS_DIR}.tgz" -C "${PROJECT_DIR}/debug_data" "${TAG}"

# Print Archive Location
echo
echo "#######################################################"
echo "Script Completed! Data has been collected and saved to:"
echo "${LOGS_DIR}"
echo "${LOGS_DIR}.tgz"
echo
