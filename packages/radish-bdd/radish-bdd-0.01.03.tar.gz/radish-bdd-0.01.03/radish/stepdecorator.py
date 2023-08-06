# -*- coding: utf-8 -*-

import re

from radish.stepregistry import StepRegistry
from radish.exceptions import StepLoadingError


def step(regex, metric_indicators=None):
    def wrapper(func):
        try:
            re.compile(regex)
        except Exception:
            raise StepLoadingError(regex)
        StepRegistry().register(regex, func, metric_indicators)
        return func
    return wrapper
