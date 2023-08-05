# -*- coding: utf-8 -*-
import os
import sys
import json
import logging
import codecs


class _System(object):

    _instance = None

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
        except:
            rst = False
        else:
            rst = True

        return rst

    def create_config_dir(self):
        self.log.warn('not implemented')

    def has_config_dir(self):
        return self.check_and_create_dir(self.get_config_dir())

    def read_configuration(self):
        if self.has_config_dir():
            filename = os.path.join(self.get_config_dir(), 'default.json')
            try:
                with codecs.open(filename, 'r', 'utf-8') as fd:
                    self._config = json.load(fd)
            except IOError:
                self._config = {}
                self.commit_configuration()
        else:
            self.log.error('Cant create configuration files.')

    def commit_configuration(self, cfg=None):
        self._config = cfg if cfg is not None else self._config
        if self.has_config_dir():
            filename = os.path.join(self.get_config_dir(), 'default.json')
            try:
                with codecs.open(filename, 'w', 'utf-8') as fd:
                    json.dump({}, fd, indent=4)
            except IOError, e:
                self.log.exception(e)
        else:
            self.log.error('Cant create configuration files.')

System = _System()
