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

import os
import re
import sys
import subprocess
import fileinput
from subprocess import Popen, PIPE
from shutil import copy2, Error
from netaddr import IPNetwork, IPAddress

from lib.config import Config
import lib.logger as logger

PATTERN_MAC = '[\da-fA-F]{2}:){5}[\da-fA-F]{2}'
CalledProcessError = subprocess.CalledProcessError


class Color:
    black = '\033[90m'
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    purple = '\033[95m'
    cyan = '\033[96m'
    white = '\033[97m'
    bold = '\033[1m'
    underline = '\033[4m'
    sol = '\033[1G'
    clr_to_eol = '\033[K'
    clr_to_bot = '\033[J'
    scroll_five = '\n\n\n\n\n'
    scroll_ten = '\n\n\n\n\n\n\n\n\n\n'
    up_one = '\033[1A'
    up_five = '\033[5A'
    up_ten = '\033[10A'
    header1 = '          ' + bold + underline
    endc = '\033[0m'


def bold(text):
    return Color.bold + text + Color.endc


def get_network_addr(ipaddr, prefix):
    return str(IPNetwork(f'{ipaddr}/{prefix}').network)


def get_netmask(prefix):
    return IPNetwork(f'0.0.0.0/{prefix}').prefixlen


def get_prefix(netmask):
    return IPAddress(netmask).netmask_bits()


def bash_cmd(cmd):
    """Run command in Bash subprocess

    Args:
        cmd (str): Command to run

    Returns:
        output (str): stdout from command
    """
    log = logger.getlogger()
    command = ['bash', '-c', cmd]
    log.debug('Run subprocess: %s' % ' '.join(command))
    output = subprocess.check_output(command, universal_newlines=True,
                                     stderr=subprocess.STDOUT).decode('utf-8')
    log.debug(output)

    return output


def backup_file(path, suffix='.orig', multi=True):
    """Save backup copy of file

    Backup copy is saved as the name of the original with the value of suffix
    appended. If multi is True, and a backup already exists, an additional
    backup is made with a numeric index value appended to the name. The backup
    copy filemode is set to read-only.

    Args:
        path (str): Path of file to backup
        suffix (str): String to append to the filename of the backup
        multi (bin): Set False to only make a backup if one does not exist
            already.
    """
    log = logger.getlogger()
    backup_path = path + suffix
    version = 0
    while os.path.exists(backup_path) and multi:
        version += 1
        backup_path += "." + str(version)
    log.debug('Make backup copy of orignal file: \'%s\'' % backup_path)
    copy2(path, backup_path)
    os.chmod(backup_path, 0o444)


def append_line(path, line, check_exists=True):
    """Append line to end of text file

    Args:
        path (str): Path of file
        line (str): String to append
        check_exists(bool): Check if line exists before appending
    """
    log = logger.getlogger()
    log.debug('Add line \'%s\' to file \'%s\'' % (line, path))

    if not line.endswith('\n'):
        line += '\n'

    exists = False
    if check_exists:
        with open(path, 'r') as file_in:
            for read_line in file_in:
                if read_line == line:
                    exists = True

    if not exists:
        with open(path, 'a') as file_out:
            file_out.write(line)


def remove_line(path, regex):
    """Remove line(s) from file containing a regex pattern

    Any lines matching the regex pattern will be removed.

    Args:
        path (str): Path of file
        regex (str): Regex pattern
    """
    log = logger.getlogger()
    log.debug('Remove lines containing regex \'%s\' from file \'%s\'' %
              (regex, path))
    for line in fileinput.input(path, inplace=1):
        if not re.match(regex, line):
            print(line, end='')


def line_in_file(path, regex, replace, backup=None):
    """If 'regex' exists in the file specified by path, then replace it with
    the value in 'replace'. Else append 'replace' to the end of the file. This
    facilitates simplified changing of a parameter to a desired value if it
    already exists in the file or adding the paramater if it does not exist.
    Inputs:
        path (str): path to the file
        regex (str): Python regular expression
        replace (str): Replacement string
        backup (str): If specified, a backup of the orginal file will be made
            if a backup does not already exist. The backup is made in the same
            directory as the original file by appending the value of backup to
            the filename.
    """
    if os.path.isfile(path):
        if backup:
            backup_file(path, multi=False)
        try:
            with open(path, 'r') as f:
                data = f.read()
        except FileNotFoundError as exc:
            print(f'File not found: {path}')
        else:
            data = data.splitlines()
            in_file = False
            # open 'r+' to maintain owner
            with open(path, 'r+') as f:
                for line in data:
                    in_line = re.search(regex, line)
                    if in_line:
                        line = re.sub(regex, replace, line)
                        in_file = True
                    f.write(line + '\n')
                if not in_file:
                    f.write(replace + '\n')


def replace_regex(path, regex, replace):
    """Replace line(s) from file containing a regex pattern

    Any lines matching the regex pattern will be removed and replaced
    with the 'replace' string.

    Args:
        path (str): Path of file
        regex (str): Regex pattern
        replace (str): String to replace matching line
    """
    log = logger.getlogger()
    log.debug('Replace regex \'%s\' with \'%s\' in file \'%s\'' %
              (regex, replace, path))
    for line in fileinput.input(path, inplace=1):
        print(re.sub(regex, replace, line), end='')


def copy_file(source, dest):
    """Copy a file to a given destination

    Args:
        source (str): Path of source file
        dest (str): Destination path to copy file to
    """
    log = logger.getlogger()
    log.debug('Copy file, source:%s dest:%s' % (source, dest))
    copy2(source, dest)


def sub_proc_launch(cmd, stdout=PIPE, stderr=PIPE):
    """Launch a subprocess and return the Popen process object.
    This is non blocking. This is useful for long running processes.
    """
    proc = Popen(cmd.split(), stdout=stdout, stderr=stderr)
    return proc


def sub_proc_exec(cmd, stdout=PIPE, stderr=PIPE, shell=False):
    """Launch a subprocess wait for the process to finish.
    Returns stdout from the process
    This is blocking
    """
    if not shell:
        cmd = cmd.split()
    proc = Popen(cmd, stdout=stdout, stderr=stderr, shell=shell)
    stdout, stderr = proc.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8'), proc.returncode


def sub_proc_display(cmd, stdout=None, stderr=None, shell=False):
    """Popen subprocess created without PIPES to allow subprocess printing
    to the parent screen. This is a blocking function.
    """
    if not shell:
        cmd = cmd.split()
    proc = Popen(cmd, stdout=stdout, stderr=stderr, shell=shell)
    proc.wait()
    rc = proc.returncode
    return rc


def sub_proc_wait(proc):
    """Launch a subprocess and display a simple time counter while waiting.
    This is a blocking wait. NOTE: sleeping (time.sleep()) in the wait loop
    dramatically reduces performace of the subprocess. It would appear the
    subprocess does not get it's own thread.
    """
    cnt = 0
    rc = None
    while rc is None:
        rc = proc.poll()
        print('\rwaiting for process to finish. Time elapsed: {:2}:{:2}:{:2}'.
              format(cnt // 3600, cnt % 3600 // 60, cnt % 60), end="")
        sys.stdout.flush()
        cnt += 1
    print('\n')
    resp, err = proc.communicate()
    print(resp)
    return rc

# def sub_proc_launch(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
#     """Launch a subprocess and return the Popen process object.
#     This is non blocking. This is useful for long running processes.
#     """
#     proc = subprocess.Popen(cmd.split(), stdout=stdout, stderr=stderr)
#     return proc
#
#
# def sub_proc_exec(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
#     """Launch a subprocess wait for the process to finish.
#     Returns stdout from the process
#     This is blocking
#     """
#     proc = subprocess.Popen(cmd.split(), stdout=stdout, stderr=stderr)
#     stdout, stderr = proc.communicate()
#     return stdout, proc.returncode
#
#
# def sub_proc_display(cmd, stdout=None, stderr=None):
#     """Popen subprocess created without PIPES to allow subprocess printing
#     to the parent screen. This is a blocking function.
#     """
#     proc = subprocess.Popen(cmd.split(), stdout=stdout, stderr=stderr)
#     proc.wait()
#     rc = proc.returncode
#     return rc
#
#
# def sub_proc_wait(proc):
#     """Launch a subprocess and display a simple time counter while waiting.
#     This is a blocking wait. NOTE: sleeping (time.sleep()) in the wait loop
#     dramatically reduces performace of the subprocess. It would appear the
#     subprocess does not get it's own thread.
#     """
#     cnt = 0
#     rc = None
#     while rc is None:
#         rc = proc.poll()
#         print('\rwaiting for process to finish. Time elapsed: {:2}:{:2}:{:2}'.
#               format(cnt // 3600, cnt % 3600 // 60, cnt % 60), end="")
#         sys.stdout.flush()
#         cnt += 1
#     print('\n')
#     resp, err = proc.communicate()
#     print(resp)
#     return rc


def scan_ping_network(network_type='all', config_path=None):
    cfg = Config(config_path)
    type_ = cfg.get_depl_netw_client_type()
    if network_type == 'pxe' or network_type == 'all':
        net_type = 'pxe'
        idx = type_.index(net_type)
        cip = cfg.get_depl_netw_client_cont_ip()[idx]
        netprefix = cfg.get_depl_netw_client_prefix()[idx]
        cidr_cip = IPNetwork(cip + '/' + str(netprefix))
        net_c = str(IPNetwork(cidr_cip).network)
        cmd = 'fping -a -r0 -g ' + net_c + '/' + str(netprefix)
        result, err = sub_proc_exec(cmd)
        print(result)

    if network_type == 'ipmi' or network_type == 'all':
        net_type = 'ipmi'
        idx = type_.index(net_type)
        cip = cfg.get_depl_netw_client_cont_ip()[idx]
        netprefix = cfg.get_depl_netw_client_prefix()[idx]
        cidr_cip = IPNetwork(cip + '/' + str(netprefix))
        net_c = str(IPNetwork(cidr_cip).network)
        cmd = 'fping -a -r0 -g ' + net_c + '/' + str(netprefix)
        result, err = sub_proc_exec(cmd)
        print(result)


def get_selection(items, choices=None, prompt='Enter a selection: ', sep='\n',
                  allow_none=False, allow_retry=False):
    """Prompt user to select a choice. Entered choice can be a member of choices or
    items, but a member of choices is always returned as choice. If choices is not
    specified a numeric list is generated. Note that if choices or items is a string
    it will be 'split' using sep. If you wish to include sep in the displayed
    choices or items, an alternate seperator can be specified.
    ex: ch, item = get_selection('Apple pie\nChocolate cake')
    ex: ch, item = get_selection('Apple pie.Chocolate cake', 'Item 1.Item 2', sep='.')
    Inputs:
        choices (str or list or tuple): Choices. If not specified, a numeric list is
        generated.
        items (str or list or tuple): Description of choices or items to select
    returns:
       ch (str): One of the elements in choices
       item (str): mathing item from items
    """
    if not items:
        return None, None
    if not isinstance(items, (list, tuple)):
        items = items.rstrip(sep)
        items = items.split(sep)
    if not choices:
        choices = [str(i) for i in range(1, 1 + len(items))]
    if not isinstance(choices, (list, tuple)):
        choices = choices.rstrip(sep)
        choices = choices.split(sep)
    if allow_none:
        choices.append('N')
        items.append('Return without making a selection.')
    if allow_retry:
        choices.append('R')
        items.append('Retry the search.')
    if len(choices) == 1:
        return choices[0], items[0]
    maxw = 1
    for ch in choices:
        maxw = max(maxw, len(ch))
    print()
    for i in range(min(len(choices), len(items))):
        print(bold(f'{choices[i]: <{maxw}}') + ' - ' + items[i])
    print()
    ch = ' '
    while not (ch in choices or ch in items):
        ch = input(f'{Color.bold}{prompt}{Color.endc}')
        if not (ch in choices or ch in items):
            print('Not a valid selection')
            print(f'Choose from {choices}')
            ch = ' '
    if ch not in choices:
        # not in choices so it must be in items
        ch = choices[items.index(ch)]
    item = items[choices.index(ch)]
    if item == 'Return without making a selection.':
        item = None
    print()
    return ch, item
