# -*- coding: utf-8 -*-

import os
import re
import copy

from radish.config import Config
from radish.feature import Feature
from radish.scenario import Scenario
from radish.step import Step
from radish.filesystemhelper import FileSystemHelper as fsh
from radish.exceptions import FeatureFileNotFoundError


class FeatureParser(object):
    def __init__(self):
        self._features = []
        self._feature_files = []
        for f in Config().feature_files:
            if os.path.isdir(f):
                self._feature_files.extend(fsh.locate(f, "*.feature"))
            else:
                self._feature_files.append(f)
        self._comment_pattern = re.compile("^[\s]*?#")
        self._feature_pattern = re.compile("Feature: ?(.*)$")
        self._scenario_pattern = re.compile("Scenario: ?(.*)$")
        self._loop_modifier_pattern = re.compile("run (\d+) times")

    def get_features(self):
        return self._features

    def parse(self):
        conf = Config()
        conf.highest_feature_id = 0
        conf.highest_scenario_id = 0
        conf.highest_step_id = 0
        conf.longest_feature_text = 0
        self._feature_id = 0
        for f in self._feature_files:
            self._features.extend(self._parse_feature(f))
        conf.highest_feature_id = self._feature_id

    def _parse_feature(self, feature_file):
        if not os.path.exists(feature_file):
            raise FeatureFileNotFoundError(feature_file)

        features = []
        in_feature = False
        feature_loop = None
        scenario_id = 0
        scenario_loop = None
        step_id = 0
        line_no = 0

        f = open(feature_file, "r")
        for l in f.readlines():
            line_no += 1
            if not l.strip() or self._comment_pattern.search(l):
                continue

            feature_match = self._feature_pattern.search(l)
            scenario_match = self._scenario_pattern.search(l)

            if feature_match:  # create new feature
                if scenario_loop:
                    self._repeat_scenario(scenario_loop[1], scenario_loop[2], features, scenario_id)
                scenario_loop = None

                if feature_loop:
                    self._repeat_feature(feature_loop[1], feature_loop[2], features)
                feature_loop = None

                in_feature = True
                self._feature_id += 1
                scenario_id = 0

                sentence, modifiers = self._get_sentence_modifiers(feature_match.group(1))
                feature_loop = modifiers["loop"]

                features.append(Feature(self._feature_id, sentence, feature_file, line_no))
                if len(feature_match.group(1)) > Config().longest_feature_text:
                    Config().longest_feature_text = len(feature_match.group(1))
            elif scenario_match:  # create new scenario
                if scenario_loop:
                    scenario_id = self._repeat_scenario(scenario_loop[1], scenario_loop[2], features, scenario_id)
                scenario_loop = None

                in_feature = False
                scenario_id += 1
                step_id = 0

                sentence, modifiers = self._get_sentence_modifiers(scenario_match.group(1))
                scenario_loop = modifiers["loop"]

                features[-1].append_scenario(Scenario(scenario_id, self._feature_id, sentence, feature_file, line_no))
                if scenario_id > Config().highest_scenario_id:
                    Config().highest_scenario_id = scenario_id
            else:  # create new step or append feature description line
                line = l.rstrip(os.linesep).strip()
                if not in_feature:
                    step_id += 1
                    features[-1].get_scenarios()[-1].append_step(Step(step_id, scenario_id, self._feature_id, line, feature_file, line_no))
                    if step_id > Config().highest_step_id:
                        Config().highest_step_id = step_id
                else:
                    features[-1].append_description_line(line)
                    if len(line) + 2 > Config().longest_feature_text:
                        Config().longest_feature_text = len(line) + 2

        if scenario_loop:
            self._repeat_scenario(scenario_loop[1], scenario_loop[2], features, scenario_id)

        if feature_loop:
            self._repeat_feature(feature_loop[1], feature_loop[2], features)

        f.close()
        return features

    def _get_sentence_modifiers(self, sentence):
        orig_sentence = sentence
        sentence_parts = [p.strip() for p in orig_sentence.split("|")]
        sentence = sentence_parts.pop(0)
        modifiers = {"loop": None}
        while sentence_parts:
            p = sentence_parts.pop(0)
            loop_match = self._loop_modifier_pattern.search(p)
            if loop_match:
                modifiers["loop"] = (True, int(loop_match.group(1)) - 1, sentence)
        if modifiers["loop"]:
            sentence += " | run 1 of %d" % (modifiers["loop"][1] + 1)
        else:
            sentence = orig_sentence
        return sentence, modifiers

    def _repeat_feature(self, times, sentence, features):
        feature = features[-1]
        for i in range(times):
            self._feature_id += 1
            new_sentence = sentence + " | run %d of %d" % (i + 2, times + 1)
            new_feature = copy.deepcopy(feature)
            new_feature.set_id(self._feature_id)
            new_feature.set_sentence(new_sentence)
            features.append(new_feature)
            if len(new_sentence) > Config().longest_feature_text:
                Config().longest_feature_text = len(new_sentence)

    def _repeat_scenario(self, times, sentence, features, last_scenario_id):
        scenario = features[-1].get_scenario(last_scenario_id)
        for i in range(times):
            last_scenario_id += 1
            new_scenario = copy.deepcopy(scenario)
            new_scenario.set_id(last_scenario_id)
            new_scenario.set_sentence(sentence + " | run %d of %d" % (i + 2, times + 1))
            features[-1].append_scenario(new_scenario)
            if last_scenario_id > Config().highest_scenario_id:
                Config().highest_scenario_id = last_scenario_id
        return last_scenario_id
