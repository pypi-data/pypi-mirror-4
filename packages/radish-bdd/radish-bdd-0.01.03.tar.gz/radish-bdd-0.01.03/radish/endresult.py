# -*- coding: utf-8 -*-


class EndResult(object):
    def __init__(self, features):
        self._features = features
        self._total_features = 0
        self._total_scenarios = 0
        self._total_steps = 0

        self._passed_features = 0
        self._passed_scenarios = 0
        self._passed_steps = 0
        self._failed_steps = 0
        self._skipped_steps = 0

        self._total_features = len(features)
        for f in features:
            if f.has_passed():
                self._passed_features += 1

            self._total_scenarios += len(f.get_scenarios())

            for s in f.get_scenarios():
                if s.has_passed():
                    self._passed_scenarios += 1

                self._total_steps += len(s.get_steps())

                for step in s.get_steps():
                    if step.has_passed():
                        self._passed_steps += 1
                    elif step.has_passed() is False:
                        self._failed_steps += 1
                    elif step.has_passed() is None:
                        self._skipped_steps += 1

    def have_all_passed(self):
        return self._total_features == self._passed_features

    def get_total_features(self):
        return self._total_features

    def get_features(self):
        return self._features

    def get_passed_features(self):
        return self._passed_features

    def get_failed_features(self):
        return self._total_features - self._passed_features

    def get_total_scenarios(self):
        return self._total_scenarios

    def get_passed_scenarios(self):
        return self._passed_scenarios

    def get_failed_scenarios(self):
        return self._total_scenarios - self._passed_scenarios

    def get_total_steps(self):
        return self._total_steps

    def get_passed_steps(self):
        return self._passed_steps

    def get_failed_steps(self):
        return self._failed_steps

    def get_skipped_steps(self):
        return self._skipped_steps
