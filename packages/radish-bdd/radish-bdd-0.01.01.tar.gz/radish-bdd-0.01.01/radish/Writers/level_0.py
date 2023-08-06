# -*- coding: utf-8 -*-

from radish.hookregistry import after, before


@before.each_feature
def print_before_feature(feature):
    pass


@before.each_scenario
def print_before_scenario(scenario):
    pass


@after.each_scenario
def print_after_scenario(scenario):
    pass


@before.each_step
def print_before_step(step):
    pass


@after.each_step
def print_after_step(step):
    pass


@after.all
def print_after_all(endResult):
    pass
