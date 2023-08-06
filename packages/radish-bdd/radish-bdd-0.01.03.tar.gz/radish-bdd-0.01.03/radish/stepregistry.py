# -*- coding: utf-8 -*-

import re

from radish.singleton import singleton


@singleton()
class StepRegistry(object):
    def __init__(self):
        self._steps = {}

    def register(self, regex, func, metric_indicators):
        self._steps[regex] = {"func": func, "metric_indicators": metric_indicators}

    def find(self, sentence):
        for regex, data in self._steps.items():
            match = re.search(regex, sentence)
            if match:
                return match, data["func"], data["metric_indicators"]
        return None, None, None
