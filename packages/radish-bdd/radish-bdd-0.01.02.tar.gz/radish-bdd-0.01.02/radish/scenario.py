# -*- coding: utf-8 -*-

from radish.config import Config
from radish.step import Step


class Scenario(object):
    def __init__(self, id, feature_id, sentence, filename, line_no):
        self._id = id
        self._feature_id = feature_id
        self._sentence = sentence
        self._filename = filename
        self._line_no = line_no
        self._steps = []

    def get_id(self):
        return self._id

    def get_feature_id(self):
        return self._feature_id

    def get_line_no(self):
        return self._line_no

    def get_sentence(self):
        return self._sentence

    def get_indentation(self):
        return "  " + " " * len(str(Config().highest_feature_id)) + "  "

    def get_duration(self):
        d = 0
        for s in self._steps:
            d += s.get_duration()
        return d

    def is_dry_run(self):
        return Config().dry_run

    def get_steps(self):
        return self._steps

    def has_passed(self):
        for s in self._steps:
            if not s.has_passed():
                return False
        return True

    def append_step(self, step):
        if isinstance(step, Step):
            self._steps.append(step)
