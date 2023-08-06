# -*- coding: utf-8 -*-

import re
from datetime import datetime
from lxml import etree

from radish.config import Config


class ReportWriter(object):
    REPORT_FILENAME = "radishtests.xml"

    def __init__(self, endResult):
        self._endResult = endResult

    def write(self):
        doc = self._generate()
        f = open(Config().xunit_file or ReportWriter.REPORT_FILENAME, "w")
        f.write(etree.tostring(doc, pretty_print=True, xml_declaration=True, encoding="utf-8"))
        f.close()

    def _generate(self):
        testsuite = etree.Element(
            "testsuite",
            name="radish",
            hostname="localhost",
            tests=str(self._endResult.get_total_steps()),
            errors="0",
            failures=str(self._endResult.get_failed_steps()),
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        )

        total_duration = 0

        for feature in self._endResult.get_features():
            for scenario in feature.get_scenarios():
                for step in scenario.get_steps():
                    testcase = etree.Element(
                        "testcase",
                        classname="%s : %s" % (feature.get_sentence(), scenario.get_sentence()),
                        name=step.get_sentence(),
                        time=str(step.get_duration())
                    )
                    if step.has_passed() is False:
                        failure = etree.Element(
                            "failure",
                            type=step.get_fail_reason().get_name(),
                            message=self._strip_ansi_text(step.get_fail_reason().get_reason())
                        )
                        failure.text = etree.CDATA(self._strip_ansi_text(step.get_fail_reason().get_traceback()))
                        testcase.append(failure)
                    testsuite.append(testcase)
                    total_duration += (step.get_duration() if step.get_duration() > 0 else 0)
        testsuite.attrib["time"] = str(total_duration)
        return etree.ElementTree(testsuite)

    def _strip_ansi_text(self, text):
        pattern = re.compile("(\\033\[\d+(?:;\d+)*m)")
        return pattern.sub("", text)
