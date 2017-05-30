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

from __future__ import nested_scopes, generators, division, absolute_import, \
    with_statement, print_function, unicode_literals

import sys
import os.path
import logging


class Logger(object):
    LOG_FILE = 'log.txt'

    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

    DEFAULT_LOG_LEVEL = getattr(logging, 'WARNING')
    LOGGER_PATH = os.path.abspath(
        os.path.dirname(os.path.abspath(__file__)) +
        os.path.sep +
        '..' +
        os.path.sep +
        '..' +
        os.path.sep +
        '..' +
        os.path.sep +
        LOG_FILE)

    def __init__(self, file_):
        self.logger = logging.getLogger(os.path.basename(file_))
        self.logger.setLevel(self.DEFAULT_LOG_LEVEL)
        self.handler = logging.FileHandler(self.LOGGER_PATH)
        self.handler.setLevel(self.DEFAULT_LOG_LEVEL)
        self.handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(self.handler)

    def set_level(self, log_level_str):
        log_levels = (
            self.DEBUG, self.INFO, self.WARNING, self.ERROR, self.CRITICAL)
        self.log_level_str = log_level_str.upper()
        if self.log_level_str not in log_levels:
            try:
                raise Exception()
            except:
                self.logger.error('Invalid log level: ' + self.log_level_str)
                sys.exit(1)

        log_level = getattr(logging, self.log_level_str)
        self.logger.setLevel(log_level)
        self.handler.setLevel(log_level)

    def get_level(self):
        return self.log_level_str

    def clear(self):
        self.logger.removeHandler(self.handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
