# Copyright (c) 2010, 2011 Linaro
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
GtkPerf is an application designed to test GTK+ performance using predefined
GTK+ widgets.

**URL:** http://gtkperf.sourceforge.net/

**Default options:** -a -c 500
"""

import re

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test


# Run tests automatically, 500 repetitions each
DEFAULT_OPTIONS = "-a -c 500"

RUNSTEPS = ["LANG=C gtkperf $(OPTIONS)"]


class GtkTestParser(TestParser):

    def parse(self, artifacts):
        PAT1 = (
            "^(?P<test_case_id>\w+)"
            " - (?P<subtest>\w*\W*\w*)"
            " - time:\W+(?P<measurement>\d+\.\d+)")
        PAT2 = (
            "^(?P<test_case_id>\w+)"
            " - time:\W+(?P<measurement>\d+\.\d+)")
        filename = "testoutput.log"
        pat1 = re.compile(PAT1)
        pat2 = re.compile(PAT2)
        with open(filename) as stream:
            for lineno, line in enumerate(stream, 1):
                match = pat1.search(line)
                if match:
                    d = match.groupdict()
                    d['test_case_id'] = "%s.%s" % (
                        d['test_case_id'],
                        d['subtest'])
                    d.pop('subtest')
                    d['test_case_id'] = d['test_case_id'].replace(" ", "_")
                    d["log_filename"] = filename
                    d["log_lineno"] = lineno
                    self.results['test_results'].append(
                        self.analyze_test_result(d))
                else:
                    match = pat2.search(line)
                    if match:
                        d = match.groupdict()
                        d["log_filename"] = filename
                        d["log_lineno"] = lineno
                        self.results['test_results'].append(
                            self.analyze_test_result(d))


installer = TestInstaller(deps=["gtkperf"])
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = GtkTestParser(appendall={'units': 'seconds', 'result': 'pass'})

testobj = Test(
    test_id="gtkperf",
    installer=installer,
    runner=runner,
    parser=parser)
