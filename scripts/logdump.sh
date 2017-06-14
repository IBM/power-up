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

usage() {
    echo "Cluster Genesis Log Dump Utility"
    echo "Usage: logdump.sh [OPTION]..."
    echo ""
    echo "  -d <dir_name>           Output directoy name"
    echo "  -t <tag_name>           Filename tag"
    echo "  -c                      Compress result into .tgz archive"
    echo "  -u                      Upload data to test server (internal only)"
    echo "  -r <remote_dir>         Remote data dir (implies -u)"
    echo "  -e <existing_data_dir>  Upload existing data to test server"
    echo "  -h                      Usage help"
}

# Parse arguments
while getopts ":d:t:cur:e:h" args; do
    case $args in
        d)
            DIR=$OPTARG
            ;;
        t)
            TAG="${OPTARG}."
            ;;
        c)
            COMPRESS=true
            ;;
        r)
            UPLOAD=true
            UPLOAD_DIR=$OPTARG
            ;;
        u)
            UPLOAD=true
            ;;
        e)
            EXISTING_DIR=$OPTARG
            ;;
        h)
            usage
            exit 0
            ;;
        ":")
            echo "Additional argument required for option $OPTARG"
            usage
            exit 1
            ;;
        \?)
            echo "unknown option -- $OPTARG"
            usage
            exit 1
            ;;
    esac
done

upload_test_data ()
{
    echo "#######################################################"
    echo "Uploading Data to Remote Repository..."

    LOCAL_DIR=$1
    if [ -z $2 ]; then
        REMOTE_DIR=$(hostname -s)
    else
        REMOTE_DIR=$2
    fi

    DEPLOYER_HOSTNAME=$(hostname -s)
    SSH_PRIVATE_KEY="$HOME/.ssh/id_rsa"
    SSH_REMOTE_USER="logdumps"
    SSH_REMOTE_HOST="9.3.210.21"
    SSH_REMOTE="${SSH_REMOTE_USER}@${SSH_REMOTE_HOST}"
    SSH_REMOTE_REPO="/home/${SSH_REMOTE_USER}/logdumps"
    WEB_REMOTE_REPO="https://github.ibm.com/cluster-genesis-dev/logdumps"
    SSH_REMOTE_SAVE="${SSH_REMOTE_REPO}/${REMOTE_DIR}"
    BASE_REMOTE_DIR=$(basename ${LOCAL_DIR})
    WEB_LINK="${WEB_REMOTE_REPO}/tree/master/${REMOTE_DIR}/${BASE_REMOTE_DIR}"

    if [ ! -f $SSH_PRIVATE_KEY ]; then
        echo "No private ssh key found at \"$SSH_PRIVATE_KEY\", creating..."
        ssh-keygen -t rsa -b 4096 -f $SSH_PRIVATE_KEY
    fi

    ssh-copy-id -i $SSH_PRIVATE_KEY $SSH_REMOTE
    ssh -i $SSH_PRIVATE_KEY $SSH_REMOTE "mkdir -p ${SSH_REMOTE_SAVE}"
    scp -i $SSH_PRIVATE_KEY -r ${LOCAL_DIR} ${SSH_REMOTE}:${SSH_REMOTE_SAVE}/.
    ssh -i $SSH_PRIVATE_KEY $SSH_REMOTE \
        "cd ${SSH_REMOTE_REPO}
        git add --all
        git commit -m 'New logdumps uploaded by ${USER}@${DEPLOYER_HOSTNAME}'
        git push origin master"
    echo ""
    echo "HTTP link to data:"
    echo "$WEB_LINK"
    echo ""
}

# If -e flag was set upload existing folder and exit
if [ ! -z $EXISTING_DIR ]; then
    if [ -d "$EXISTING_DIR" ]; then
        upload_test_data $EXISTING_DIR $UPLOAD_DIR
        exit 0
    else
        echo "ERROR: $EXISTING_DIR not found!"
        exit 1
    fi
fi

# Set date
DATE=$(date +%Y-%m-%dT%H%M%z)

# Get hostname
HOST=$(hostname -s)

# Create DIR is user didn't set with arg
if [ -z $DIR ]; then
    DIR="logdump.$HOST.$DATE"
fi

# Get cluster-genesis top level directory
PROJECT_DIR=$(git rev-parse --show-toplevel)
PLAYBOOKS="${PROJECT_DIR}/playbooks"

# Create Directories
if [ ! -d "${PROJECT_DIR}/logdumps" ]; then
    mkdir "${PROJECT_DIR}/logdumps"
fi
LOGS_DIR="${PROJECT_DIR}/logdumps/${DIR}"
mkdir $LOGS_DIR

# Save logdump.sh stdout and stderr to file
exec >  >(tee -ia ${LOGS_DIR}/logdump.log)
exec 2> >(tee -ia ${LOGS_DIR}/logdump.log >&2)

# Get container SSH connection info from ansible hosts file
SSH_USER=$(grep -oh "ansible_user=[^ ]*" "${PLAYBOOKS}/hosts" | \
    awk -F = '{print $2}')
SSH_HOST=$(grep -oh "ansible_host=[^ ]*" "${PLAYBOOKS}/hosts" | \
    awk -F = '{print $2}')
SSH_KEY=$(grep -oh "ansible_ssh_private_key_file=[^ ]*" \
    "${PLAYBOOKS}/hosts" | awk -F = '{print $2}')

# Get mgmt switch SSH userids
MGMT_SWITCH_SSH_USER=$(awk '/^userid-mgmt-switch:/{print $2}' \
    ${PROJECT_DIR}/config.yml)
# If no uncomment key exists get _first_ commented key
if [ -z $MGMT_SWITCH_SSH_USER ]; then
    MGMT_SWITCH_SSH_USER=$(awk '/userid-mgmt-switch:/{print $2}' \
        ${PROJECT_DIR}/config.yml)
    MGMT_SWITCH_SSH_USER=(${MGMT_SWITCH_SSH_USER[@]})
fi

# Get data switch SSH userids
DATA_SWITCH_SSH_USER=$(awk '/^userid-data-switch:/{print $2}' \
    ${PROJECT_DIR}/config.yml)
# If no uncomment key exists get _first_ commented key
if [ -z $DATA_SWITCH_SSH_USER ]; then
    DATA_SWITCH_SSH_USER=$(awk '/userid-data-switch:/{print $2}' \
        ${PROJECT_DIR}/config.yml)
    DATA_SWITCH_SSH_USER=(${DATA_SWITCH_SSH_USER[@]})
fi

# Local Deployer File Pointers
DEPLOYER_INFO_SAVE="${LOGS_DIR}/${TAG}deployer.info.txt"

GIT_REPO_INFO_SAVE="${LOGS_DIR}/${TAG}deployer.git_diff_head.txt"

CONFIG_PATH="${PROJECT_DIR}/config.yml"
CONFIG_SAVE="${LOGS_DIR}/${TAG}deployer.config.yml"

CONFIG_BACKUP_PATH="${PROJECT_DIR}/config-backup.yml"
CONFIG_BACKUP_SAVE="${LOGS_DIR}/${TAG}deployer.config-backup.yml"

INV_DEPLOYER_PATH="/var/oprc/inventory.yml"
INV_DEPLOYER_SAVE="${LOGS_DIR}/${TAG}deployer.inventory.yml"

ANSIBLE_LOG_PATH="${PLAYBOOKS}/ansible.log"
ANSIBLE_LOG_SAVE="${LOGS_DIR}/${TAG}deployer.ansible.log"

LXC_CONF_PATH="${PLAYBOOKS}/lxc.conf"
LXC_CONF_SAVE="${LOGS_DIR}/${TAG}deployer.lxc.conf"

MGMT_SWITCH_SAVE="${LOGS_DIR}/${TAG}mgmt_switch"
DATA_SWITCH_SAVE="${LOGS_DIR}/${TAG}data_switch"

PASSIVE_SWITCH_MAC_TABLES_PATH="${PROJECT_DIR}/passive"
PASSIVE_SWITCH_MAC_TABLES_SAVE="${LOGS_DIR}/passive"

# Container File Pointers
INV_CONTAINER_PATH="~/cluster-genesis/inventory.yml"
INV_CONTAINER_SAVE="${LOGS_DIR}/${TAG}container.inventory.yml"

GENESIS_LOG_PATH="~/cluster-genesis/log.txt"
GENESIS_LOG_SAVE="${LOGS_DIR}/${TAG}container.log.txt"

# Functions to save files
save_local_file ()
{
    if [ -f $1 ] || [ -d $1 ]; then
        echo "Saving $1 to $2"
        cp -rp $1 $2
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

get_config_key ()
{
    KEY=$1
    FOUND=false
    INDEX=0
    while IFS='' read line; do
        if [[ $line == $"$KEY:"* ]]; then
            FOUND=true
            continue
        fi
        if [ "$FOUND" = true ]; then
            if [[ $line =~ ^[[:space:]]*# ]]; then
                continue
            elif [[ $line == $"    "* ]]; then
                TEST=$(awk '{split($0, a); print a[2]}' <<< $line)
                if [ ! -z $TEST ]; then
                    config_value[$INDEX]=$TEST
                    INDEX=($INDEX+1)
                fi
            else
                FOUND=false
            fi
        fi
    done < "$CONFIG_PATH"
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
save_local_file $PASSIVE_SWITCH_MAC_TABLES_PATH $PASSIVE_SWITCH_MAC_TABLES_SAVE

# Save off files in container
save_container_file $INV_CONTAINER_PATH $INV_CONTAINER_SAVE
save_container_file $GENESIS_LOG_PATH $GENESIS_LOG_SAVE

# Save mgmt switch(es) configuration
get_config_key "ipaddr-mgmt-switch"
for ip in "${config_value[@]}"; do
    echo "Collecting mgmt switch config from ${MGMT_SWITCH_SSH_USER}@$ip"
    if ping -c 1 $ip; then
        ssh ${MGMT_SWITCH_SSH_USER}@$ip \
            'en; conf t; line vty length 0; sh run' \
            > "$MGMT_SWITCH_SAVE.$ip.log" || \
            echo "WARNING: ssh returned non-zero return code!"
    else
        echo "WARNING: Switch $ip does not ping!"
    fi
done

# Save data switch(es) configuration
get_config_key "ipaddr-data-switch"
for ip in "${config_value[@]}"; do
    echo "Collecting data switch config from ${DATA_SWITCH_SSH_USER}@$ip"
    if ping -c 1 $ip; then
        ssh ${DATA_SWITCH_SSH_USER}@$ip \
            'cli en show\ running-config show\ vlan show\ mac-address-table' \
            > "$DATA_SWITCH_SAVE.$ip.log" || \
            echo "WARNING: ssh returned non-zero return code!"
    else
        echo "WARNING: Switch $ip does not ping!"
    fi
done

# Tar & compress logs
if [ ! -z $COMPRESS ]; then
    tar -cvzf "${LOGS_DIR}.tgz" -C "${PROJECT_DIR}/logdumps" "${DIR}"
fi

# Print Archive Location
echo
echo "#######################################################"
echo "Script Completed! Data has been collected and saved to:"
echo "${LOGS_DIR}"
if [ ! -z $COMPRESS ]; then
    echo "${LOGS_DIR}.tgz"
fi
echo

# Upload data to test server if -u argument was passed
if [ ! -z $UPLOAD ]; then
    upload_test_data $LOGS_DIR $UPLOAD_DIR
fi
