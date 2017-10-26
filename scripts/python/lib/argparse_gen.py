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

from enum import Enum
from argparse import ArgumentParser, RawTextHelpFormatter

PROJECT = 'Cluster Genesis'
SETUP_CMD = 'setup'
CONFIG_CMD = 'config'
VALIDATE_CMD = 'validate'
DEPLOY_CMD = 'deploy'
SETUP_DESC = 'Setup deployment environment (requires root privileges)'
CONFIG_DESC = 'Configure deployment environment'
VALIDATE_DESC = 'Validate deployment environment'
DEPLOY_DESC = 'Deploy cluster'
GITHUB = 'https://github.com/open-power-ref-design-toolkit/cluster-genesis'
EPILOG = 'home page:\n  %s' % GITHUB


class Cmd(Enum):
    SETUP = SETUP_CMD
    CONFIG = CONFIG_CMD
    VALIDATE = VALIDATE_CMD
    DEPLOY = DEPLOY_CMD


def get_args():
    """Get 'gen' command arguments"""

    parser = ArgumentParser(
        description=PROJECT,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers()

    # Subparsers
    parser_setup = subparsers.add_parser(
        SETUP_CMD,
        description='%s - %s' % (PROJECT, SETUP_DESC),
        help=SETUP_DESC,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter)
    parser_config = subparsers.add_parser(
        CONFIG_CMD,
        description='%s - %s' % (PROJECT, CONFIG_DESC),
        help=CONFIG_DESC,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter)
    parser_validate = subparsers.add_parser(
        VALIDATE_CMD,
        description='%s - %s' % (PROJECT, VALIDATE_DESC),
        help=VALIDATE_DESC,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter)
    parser_deploy = subparsers.add_parser(
        DEPLOY_CMD,
        description='%s - %s' % (PROJECT, DEPLOY_DESC),
        help=DEPLOY_DESC,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter)

    # 'setup' subcommand arguments
    parser_setup.set_defaults(
        setup=True)

    parser_setup.add_argument(
        '--bridges',
        action='store_true',
        help='Create deployer bridges')

    parser_setup.add_argument(
        '--gateway',
        action='store_true',
        help='Configure PXE network gateway and NAT record')

    parser_setup.add_argument(
        '-a', '--all',
        action='store_true',
        help='Apply all actions')

    # 'config' subcommand arguments
    parser_config.set_defaults(
        config=True)

    parser_config.add_argument(
        '--create-container',
        metavar='<Container name>',
        help='Create deployer container')

    # 'validate' subcommand arguments
    parser_validate.set_defaults(
        validate=True)

    parser_validate.add_argument(
        '--config-file',
        action='store_true',
        help='Schema and logic validation')

    # 'deploy' subcommand arguments
    parser_deploy.set_defaults(
        deploy=True)

    parser_deploy.add_argument(
        '-a', '--all',
        action='store_true',
        help='Apply all actions')

    return parser


def get_parsed_args():
    """Get parsed 'gen' command arguments"""

    return get_args().parse_args()
