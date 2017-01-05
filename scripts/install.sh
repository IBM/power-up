#!/bin/bash
# Copyright 2016 IBM Corp.
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
DISTRIB_RELEASE=$(lsb_release -sr)
sudo apt-get -y install python-pip python-dev libffi-dev libssl-dev \
    python-netaddr ipmitool
if [[ $DISTRIB_RELEASE == "14.04" ]]; then
    sudo apt-get -y install lxc-dev
fi
sudo -H pip install --upgrade pip
sudo -H pip install --upgrade setuptools
sudo -H pip install --upgrade wheel
if [[ $DISTRIB_RELEASE == "14.04" ]]; then
    sudo -H pip install lxc-python2
fi
sudo -H pip install virtualenv
virtualenv --no-wheel --system-site-packages deployenv
source deployenv/bin/activate
pip install ansible orderedattrdict
deactivate
