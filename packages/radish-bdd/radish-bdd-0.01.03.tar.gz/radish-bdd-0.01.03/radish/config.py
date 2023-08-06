# -*- coding: utf-8 -*-

import os

from radish.exceptions import BasedirNotFoundError


class Config(object):
    _instance = None

    class __Config(object):
        def SetBasedir(self, basedir):
            if not os.path.exists(basedir) or not os.path.isdir(basedir):
                raise BasedirNotFoundError(basedir)
            self.basedir = basedir

    def __new__(cls):
        if not Config._instance:
            Config._instance = Config.__Config()
        return Config._instance

    def __getattr__(self, key):
        return getattr(self._instance, key)

    def __setattr__(self, key, value):
        return setattr(self._instance, key, value)
