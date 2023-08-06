# -*- coding: utf-8 -*-

import sys

from radish.config import Config
from radish.hookregistry import after, before
from radish.filesystemhelper import FileSystemHelper as fsh


@before.each_feature
def print_before_feature(feature):
    if not feature.is_dry_run():
        print(feature.get_indentation() + "%*d. " % (len(str(Config().highest_feature_id)), feature.get_id()) + feature.get_sentence() + " " * (Config().longest_feature_text - len(feature.get_sentence())) + " " * 10 + "# " + fsh.filename(feature.get_filename()))
        for l in feature.get_description().splitlines():
            print(feature.get_indentation() + " " * len(str(Config().highest_feature_id)) + "  " + l)
        print("")


@before.each_scenario
def print_before_scenario(scenario):
    if not scenario.is_dry_run():
        print(scenario.get_indentation() + "%*d. %s" % (len(str(Config().highest_scenario_id)), scenario.get_id(), scenario.get_sentence()))


@after.each_scenario
def print_after_scenario(scenario):
    if not scenario.is_dry_run():
        print("")


@before.each_step
def print_before_step(step):
    if not step.is_dry_run():
        print(step.get_indentation() + "%*d. %s" % (len(str(Config().highest_step_id)), step.get_id(), step.get_sentence_splitted()[1]))


@after.each_step
def print_after_step(step):
    if not step.is_dry_run():
        splitted = step.get_sentence_splitted()
        sys.stdout.write("\033[A\033[K" * splitted[0])

        if step.has_passed() is None and Config().no_skipped_steps:
            return

        print(step.get_indentation() + "%*d. %s" % (len(str(Config().highest_step_id)), step.get_id(), splitted[1]))

        if step.has_passed() is False:
            if Config().with_traceback:
                for l in step.get_fail_reason().get_traceback().splitlines():
                    print(step.get_sentence_indentation() + l)
            else:
                print(step.get_sentence_indentation() + step.get_fail_reason().get_name() + ": " + step.get_fail_reason().get_reason())


@after.all
def print_after_all(endResult):
    if not Config().dry_run:
        feature_text = str(endResult.get_passed_features()) + " passed"
        if endResult.get_failed_features() > 0:
            feature_text += ", " + str(endResult.get_failed_features()) + " failed"

        scenario_text = str(endResult.get_passed_scenarios()) + " passed"
        if endResult.get_failed_scenarios() > 0:
            scenario_text += ", " + str(endResult.get_failed_scenarios()) + " failed"

        step_text = str(endResult.get_passed_steps()) + " passed"
        if endResult.get_failed_steps() > 0:
            step_text += ", " + str(endResult.get_failed_steps()) + " failed"
        if endResult.get_skipped_steps() > 0:
            step_text += ", " + str(endResult.get_skipped_steps()) + " skipped"

        print(str(endResult.get_total_features()) + " features (%s" % (feature_text) + ")")
        print(str(endResult.get_total_scenarios()) + " scenarios (%s" % (scenario_text) + ")")
        print(str(endResult.get_total_steps()) + " steps (%s" % (step_text) + ")")

        if not Config().no_duration:
            duration = 0.0
            for f in endResult.get_features():
                duration += f.get_duration()
            print("(finished within %d minutes and %.2f seconds)" % (duration / 60, float(duration) % 60.0))
