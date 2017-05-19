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
# 2) Apply needed patches to buildroot(old ssh, new configs etc)
#
# Exit 0 on success; 1 on failure
#
set -e

#if buildroot is already pulled, do not try to reclone, patch
#application will fail
if [ -d buildroot ]; then
    echo "buildroot directory already exists"
    exit
fi

#pull down open-power version of buildroot
#checkout March tag, avoid master in case future updates break build
git clone --branch 2017.02 https://github.com/open-power/buildroot.git

./patch_source.sh buildroot

