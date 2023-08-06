# -*- coding: utf-8 -*-

from radish.singleton import singleton


@singleton()
class UtilRegistry(object):
    def __init__(self):
        self._utils = {}

    def register(self, util, func):
        self._utils[util] = func

    def has_util(self, util):
        return util in self._utils

    def call_util(self, util, *args, **kw):
        if self.has_util(util):
            return self._utils[util](*args, **kw)
        return None


def utils(util):
    def _wrapper(func):
        UtilRegistry().register(util, func)
        return func
    return _wrapper
