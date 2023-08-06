# -*- coding: utf-8 -*-
'''
    Copyright (C) 2013  Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from kidelib.default import configuration, decompress

import os
import sys
import json
import logging
import codecs


class _System(object):

    _instance = None

    _config_sections = [
        'editor',
        'menu'
    ]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_System, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @property
    def config(self):
        if hasattr(self, '_config') is False:
            self.read_configuration()
        return self._config

    @property
    def log(self):
        return self.get_logger()

    def get_logger(self):
        if hasattr(self, 'logger') is False:
            self.logger = logging.getLogger()
            handler = logging.StreamHandler(sys.stdout)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
        return self.logger

    def get_config_dir(self):
        return os.environ.get(
            'KIDE_ENV',
            os.path.expanduser('~/.config/kide')
        )

    def check_and_create_dir(self, path):
        rst = None
        self.log.info('Check if exist %s directory' % path)

        try:
            if not os.path.exists(path) and \
               self.check_and_create_dir(os.path.dirname(path)):
                os.mkdir(path)
        except Exception, e:
            System.log.exception(e)
            rst = False
        else:
            rst = True

        return rst

    def has_config_dir(self):
        return self.check_and_create_dir(self.get_config_dir())

    def read_default_config(self, section):
        config = None

        try:
            config = decompress(configuration.get('%s.json' % section))
        except Exception, e:
            System.log.exception(e)
            config = '{}'
        finally:
            config = json.loads(config)

        return config

    def read_configuration(self):
        self._config = {}

        for section in self._config_sections:
            self._config.update({
                section: self._read_configuration(section)
            })

    def _read_configuration(self, section):
        config = {}

        if self.has_config_dir():
            filename = os.path.join(self.get_config_dir(), '%s.json' % section)
            try:
                with codecs.open(filename, 'r', 'utf-8') as fd:
                    config = json.load(fd)
            except IOError:
                config = self.read_default_config(section)
                self._commit_configuration(section, config)
        else:
            self.log.error('Cant create configuration files.')

        return config

    def commit_configuration(self):
        for section, config in self._config.items():
            self._commit_configuration(section, config)

    def _commit_configuration(self, section, config):
        if self.has_config_dir():
            filename = os.path.join(self.get_config_dir(), '%s.json' % section)
            try:
                with codecs.open(filename, 'w', 'utf-8') as fd:
                    json.dump(config, fd, indent=4)
            except IOError, e:
                self.log.exception(e)
        else:
            self.log.error('Cant create configuration files.')

System = _System()
