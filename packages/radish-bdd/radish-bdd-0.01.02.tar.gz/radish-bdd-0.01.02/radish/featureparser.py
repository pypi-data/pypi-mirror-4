# -*- coding: utf-8 -*-

import os
import re

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
        scenario_id = 0
        step_id = 0
        line_no = 0

        # FIXME: compile regex patterns
        f = open(feature_file, "r")
        for l in f.readlines():
            line_no += 1
            if not l.strip() or re.search("^[\s]*?#", l):
                continue

            feature_match = re.search("Feature: ?(.*)$", l)
            scenario_match = re.search("Scenario: ?(.*)$", l)

            if feature_match:  # create new feature
                in_feature = True
                self._feature_id += 1
                scenario_id = 0
                features.append(Feature(self._feature_id, feature_match.group(1), feature_file, line_no))
                if len(feature_match.group(1)) > Config().longest_feature_text:
                    Config().longest_feature_text = len(feature_match.group(1))
            elif scenario_match:  # create new scenario
                in_feature = False
                scenario_id += 1
                step_id = 0
                features[-1].append_scenario(Scenario(scenario_id, self._feature_id, scenario_match.group(1), feature_file, line_no))
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

        f.close()
        return features
