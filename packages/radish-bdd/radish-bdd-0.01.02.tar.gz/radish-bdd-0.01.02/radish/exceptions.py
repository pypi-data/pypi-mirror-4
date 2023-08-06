# -*- coding: utf-8 -*-

from radish.colorful import colorful


class RadishError(Exception):
    pass


class StepLoadingError(RadishError):
    """Raised when a step decorator regex is not valid to compile"""
    def __init__(self, regex):
        self.regex = regex

    def __str__(self):
        return colorful.red("The step decorator regex '%s' is not valid to compile" % (self.regex))


class StepDefinitionNotFoundError(RadishError):
    """Raised when a step definition could not be found"""
    def __init__(self, step_sentence):
        self.step_sentence = step_sentence

    def __str__(self):
        return colorful.red("The step definition for the step '%s' could not be found" % (self.step_sentence))


class FeatureFileNotFoundError(RadishError):
    """Raised when a feature file could not be found"""
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return colorful.red("The feature file '%s' could not be found" % (self.path))


class BasedirNotFoundError(RadishError):
    """Raised when the basedir could not be found"""
    def __init__(self, basedir):
        self.basedir = basedir

    def __str__(self):
        return colorful.red("The basedir '%s' could not be found" % (self.basedir))


class StepDefinitionFileNotFoundError(RadishError):
    """Raised when the step definition file could not be found"""
    def __init__(self, root, pattern):
        self.root = root
        self.pattern = pattern

    def __str__(self):
        return colorful.red("The step definition file '%s' could not be found in the directory '%s'" % (self.pattern, self.root))


class WriterNotFoundError(RadishError):
    """Raised when the writer could not be found"""
    def __init__(self, level):
        self.level = level

    def __str__(self):
        return colorful.red("The writer for verbosity level '%d' could not be found!" % self.level)


class ValidationError(RadishError):
    """Raised when a validation error occured during run"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return colorful.bold_red(self.msg)
