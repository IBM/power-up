"""Cluster Genesis 'gen' command argument parser"""

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

from argparse import ArgumentParser, RawTextHelpFormatter

PROJECT = 'Cluster Genesis'
DEPLOYER_CMD = 'deployer'

DEPLOYER_DESC = 'Teardown {} deployer elements'.format(PROJECT)
DEPLOYER_NETWORKS_HELP = ('Deletes {} created interfaces and bridges. \nRemoves {} '
                          'added addresses from external interfaces.'.format(PROJECT, PROJECT))
GITHUB = 'https://github.com/open-power-ref-design-toolkit/cluster-genesis'
EPILOG = 'home page:\n  %s' % GITHUB


def get_args():
    """Get 'teardown' command arguments"""

    parser = ArgumentParser(
        description=PROJECT,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers()

    # Subparsers
    parser_deployer = subparsers.add_parser(
        DEPLOYER_CMD,
        description='%s - %s' % (PROJECT, DEPLOYER_DESC),
        help=DEPLOYER_DESC,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter)

    # 'deployer' subcommand arguments
    parser_deployer.set_defaults(
        deployer=True)

    parser_deployer.add_argument(
        '--networks',
        action='store_true',
        help=DEPLOYER_NETWORKS_HELP)

    parser_deployer.add_argument(
        '--gateway',
        action='store_true',
        help='Delete deployer network gateway and NAT record')

    parser_deployer.add_argument(
        '--container',
        action='store_true',
        help='Destroy the {} container.'.format(PROJECT))

    parser_deployer.add_argument(
        '-a, --all',
        action='store_true',
        help='Apply all actions')

    return parser


def get_parsed_args():
    """Get parsed 'gen' command arguments"""

    return get_args().parse_args()
