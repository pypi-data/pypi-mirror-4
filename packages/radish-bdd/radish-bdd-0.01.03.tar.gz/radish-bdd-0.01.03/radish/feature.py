# -*- coding: utf-8 -*-

import os

from radish.config import Config
from radish.scenario import Scenario


class Feature(object):
    def __init__(self, id, sentence, filename, line_no):
        self._id = id
        self._sentence = sentence
        self._filename = filename
        self._line_no = line_no
        self._scenarios = []
        self._description = ""

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    def get_line_no(self):
        return self._line_no

    def get_sentence(self):
        return self._sentence

    def set_sentence(self, sentence):
        self._sentence = sentence

    def get_filename(self):
        return self._filename

    def get_description(self):
        return self._description

    def get_indentation(self):
        return "  "

    def get_duration(self):
        d = 0
        for s in self._scenarios:
            d += s.get_duration()
        return d

    def is_dry_run(self):
        return Config().dry_run

    def get_scenarios(self):
        return self._scenarios

    def get_scenario(self, id):
        for s in self._scenarios:
            if s.get_id() == id:
                return s
        return None

    def has_passed(self):
        for s in self._scenarios:
            if not s.has_passed():
                return False
        return True

    def append_scenario(self, scenario):
        if isinstance(scenario, Scenario):
            self._scenarios.append(scenario)

    def append_description_line(self, line):
        if self._description == "":
            self._description = line
        else:
            self._description += os.linesep + line
