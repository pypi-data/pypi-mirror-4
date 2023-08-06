# -*- coding: utf-8 -*-

import os

from radish.config import Config
from radish.stepregistry import StepRegistry
from radish.filesystemhelper import FileSystemHelper as fsh
from radish.exceptions import StepDefinitionFileNotFoundError, StepDefinitionNotFoundError, WriterNotFoundError


class Loader(object):
    def __init__(self, features):
        self._features = features

    def load(self):
        self._load_terrain()
        self._load_step_definitions()
        self._load_writer()
        self._load_logger()

    def _load_terrain(self):
        fsh.import_module(Config().basedir, "terrain.py")

    def _load_step_definitions(self):
        if not fsh.locate(Config().basedir, "steps.py"):
            raise StepDefinitionFileNotFoundError(Config().basedir, "steps.py")

        fsh.import_module(Config().basedir, "steps.py")
        self._merge_steps_with_definitions()

    def _load_writer(self):
        if not fsh.locate(Config().basedir, "writer.py"):
            level = int(Config().verbosity)
            try:
                fsh.import_module(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Writers"), "level_%d.py" % level, no_modules_error=True)
            except ImportError:
                raise WriterNotFoundError(level)
        else:
            fsh.import_module(Config().basedir, "writer.py")

    def _load_logger(self):
        if fsh.locate(Config().basedir, "logger.py"):
            fsh.import_module(Config().basedir, "logger.py")

    def _merge_steps_with_definitions(self):
        sr = StepRegistry()
        for feature in self._features:
            for scenario in feature.get_scenarios():
                for step in scenario.get_steps():
                    match, func = sr.find(step.get_sentence())
                    if match and func:
                        step.set_function(func)
                        step.set_match(match)
                    else:
                        raise StepDefinitionNotFoundError(step.get_sentence())
