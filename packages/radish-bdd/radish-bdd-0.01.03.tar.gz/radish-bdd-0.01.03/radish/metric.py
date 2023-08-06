# -*- coding: utf-8 -*-


class Metric(object):
    def __init__(self, features):
        self._features = features

    def calculate(self):
        metric = {}
        for feature in self._features:
            for scenario in feature.get_scenarios():
                for step in scenario.get_steps():
                    for indicator in step.get_metric_indicators():
                        try:
                            metric[indicator] += 1
                        except KeyError:
                            metric[indicator] = 1
        return metric
