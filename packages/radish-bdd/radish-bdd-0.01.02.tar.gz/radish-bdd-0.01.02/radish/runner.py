# -*- coding: utf-8 -*-

import sys

from radish.config import Config
from radish.hookregistry import HookRegistry
from radish.endresult import EndResult


class Runner(object):
    def __init__(self, features):
        self._features = features

    def run(self):
        hr = HookRegistry()
        hr.call_hook("before", "all")

        abort = False
        interrupted = False
        for f in self._features:
            hr.call_hook("before", "feature", f)

            for s in f.get_scenarios():
                hr.call_hook("before", "scenario", s)
                skip_remaining_steps = False

                for step in s.get_steps():
                    hr.call_hook("before", "step", step)

                    if not skip_remaining_steps and not interrupted:
                        try:
                            passed = step.run()
                            if not passed and not Config().dry_run:
                                skip_remaining_steps = True
                                if Config().abort_fail:
                                    abort = True
                        except KeyboardInterrupt:
                            interrupted = True
                            sys.stdout.write("\r")

                    hr.call_hook("after", "step", step)
                hr.call_hook("after", "scenario", s)
                if abort:  # if -a is set
                    break
            hr.call_hook("after", "feature", f)
            if abort:  # if -a is set
                break
        endResult = EndResult(self._features)
        hr.call_hook("after", "all", endResult)
        return endResult
