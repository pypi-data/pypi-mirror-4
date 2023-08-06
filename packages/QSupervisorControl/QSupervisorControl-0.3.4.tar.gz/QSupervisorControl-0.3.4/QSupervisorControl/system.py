# -*- coding: utf-8 -*-
import sys
import logging


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
    def log(self):
        return self.get_logger()

    def get_logger(self):
        if hasattr(self, 'logger') is False:
            self.logger = logging.getLogger()
            handler = logging.StreamHandler(sys.stdout)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)


System = _System()
