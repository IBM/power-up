#! /usr/bin/env python
# Copyright 2018 IBM Corp.
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

from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals

from subprocess import Popen, PIPE
import argparse
import os
import re
import sys
import time

import lib.logger as logger
from repos import local_epel_repo, remote_nginx_repo
from software_hosts import get_ansible_inventory


def _sub_proc_launch(cmd, stdout=PIPE, stderr=PIPE):
    data = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    return data


def _sub_proc_exec(cmd, stdout=PIPE, stderr=PIPE):
    data = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = data.communicate()
    return stdout, stderr


def _sub_proc_display(cmd, stat_re=None, stdout=PIPE, stderr=PIPE):
    proc = Popen(cmd.split(), stdout=stdout, stderr=stderr)
    rc = None
    ret = None
    while rc is None:
        resp = proc.stderr.readline()
        resp = unicode(resp, 'utf-8')
        resp = resp.replace('\n', '   ')
        r = re.search(stat_re, resp)
        if r:
            ret = r
        print(u'\r' + resp, end="")
        rc = proc.poll()
    print('')
    return resp, ret


def _sub_proc_wait(proc):
    cnt = 0
    rc = None
    while rc is None:
        rc = proc.poll()
        print('\rwaiting for process to finish. Time elapsed: {:2}:{:2}:{:2}'.
              format(cnt // 3600, cnt % 3600 // 60, cnt % 60), end="")
        sys.stdout.flush()
        time.sleep(1)
        cnt += 1
    print('\n')
    resp, err = proc.communicate()
    print(resp)
    return rc


class software(object):
    """ Software installation class. The setup method is used to setup
    repositories, download files to the installer node or perform other
    initialization activities. The install method implements the actual
    installation.
    """
    def __init__(self):
        self.log = logger.getlogger()
        self.yum_powerup_repo_files = []

    def setup(self):
        # Get Anaconda
        if not os.path.exists('/srv/anaconda'):
            os.mkdir('/srv/anaconda')
        if not os.path.isfile('/srv/anaconda/Anaconda2-5.1.0-Linux-ppc64le.sh'):
            self.log.info('Downloading Anaconda')
            cmd = ('wget https://repo.continuum.io/archive/Anaconda2-5.1.0-Linux-'
                   'ppc64le.sh --directory-prefix=/srv/anaconda/')
            resp, stat = _sub_proc_display(cmd, stat_re=r'saved \[(\d+)/(\d+)\]')
            if stat and stat.group(1) == stat.group(2):
                self.log.info('PowerAI base downloaded succesfully')
            else:
                self.log.error('Failed to download PowerAI base')
        else:
            self.log.info('Anaconda already downloaded')

        # Get PowerAI base
        if not os.path.exists('/srv/powerai-rpm'):
            os.mkdir('/srv/powerai-rpm')
        if not os.path.isfile('/srv/powerai-rpm/mldl-repo-local-5.1.0-201804110899'
                              '.fd91856.ppc64le.rpm'):
            self.log.info('Downloading PowerAI base')
            cmd = ('wget --directory-prefix=/srv/powerai-rpm http://ausgsa.ibm.com'
                   '/projects/m/mldl-repo/releases/v1r5m1/rhel/mldl-repo-local-5.1.'
                   '0-201804110899.fd91856.ppc64le.rpm')
            resp, stat = _sub_proc_display(cmd, stat_re=r'saved \[(\d+)/(\d+)\]')
            if stat and stat.group(1) == stat.group(2):
                self.log.info('PowerAI base downloaded succesfully')
            else:
                self.log.error('Failed to download PowerAI base')
        else:
            self.log.info('PowerAI base already downloaded')

        repo = local_epel_repo()

        # repo.yum_create_remote()
        # repo.create_dirs()
        # repo.sync()
        # repo.create_meta()
        # repo.yum_create_local()
        self.yum_powerup_repo_files.append(repo.get_yum_client_powerup())

        self.log.debug(self.yum_powerup_repo_files[0]['filename'])
        self.log.debug(self.yum_powerup_repo_files[0]['content'])

        # nginx_repo = remote_nginx_repo()
        # nginx_repo.yum_create_remote()

        return
        # Check if nginx installed. Install if necessary.
        cmd = 'nginx -v'
        resp, err = _sub_proc_exec(cmd)
        if 'nginx version' in err:
            print('nginx is installed:\n{}'.format(resp))
        else:
            cmd = 'yum -y install nginx'
            resp, err = _sub_proc_exec(cmd)
            if err != 0:
                self.log.error('Failed installing nginx')
                self.log.error(resp)
                sys.exit(1)
            else:
                # Fire it up
                cmd = 'nginx'
                resp, err = _sub_proc_exec(cmd)
                if err != 0:
                    self.log.error('Failed starting nginx')
                    sys.exit(1)

        cmd = 'curl -I 127.0.0.1'
        resp, err = _sub_proc_exec(cmd)
        if 'HTTP/1.1 200 OK' in resp:
            self.log.info('nginx is running:\n')

        # Setup firewall to allow http
        fw_err = 0
        cmd = 'systemctl status firewalld.service'
        resp, err = _sub_proc_exec(cmd)
        if 'Active: active (running)' in resp.splitlines()[2]:
            self.log.debug('Firewall is running')
        else:
            cmd = 'systemctl enable firewalld.service'
            resp, err = _sub_proc_exec(cmd)
            if err != 0:
                fw_err += 1
                self.log.error('Failed to enable firewall')

            cmd = 'systemctl start firewalld.service'
            resp, err = _sub_proc_exec(cmd)
            if err != 0:
                fw_err += 10
                self.log.error('Failed to start firewall')
        cmd = 'firewall-cmd --permanent --add-service=http'
        resp, err = _sub_proc_exec(cmd)
        if 'ALREADY_ENABLED: http' not in err:
            fw_err += 100
            self.log.error('Failed to enable http service on firewall')

        cmd = 'firewall-cmd --reload'
        resp, err = _sub_proc_exec(cmd)
        if 'success' not in resp:
            fw_err += 1000
            self.log.error('Error attempting to restart firewall')
        if fw_err == 0:
            self.log.info('Firewall is running and configured for http')

        print('Good to go')

    def install(self):
        cmd = 'ansible -i {} -m ping all'.format(get_ansible_inventory())
        resp, err = _sub_proc_exec(cmd)
        print(resp)
        print('All done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['setup', 'install'],
                        help='Action to take: setup or install')

    parser.add_argument('--print', '-p', dest='log_lvl_print',
                        help='print log level', default='info')

    parser.add_argument('--file', '-f', dest='log_lvl_file',
                        help='file log level', default='info')

    args = parser.parse_args()

    logger.create(args.log_lvl_print, args.log_lvl_file)

    soft = software()

    if args.action == 'setup':
        soft.setup()
    elif args.action == 'install':
        soft.install()
