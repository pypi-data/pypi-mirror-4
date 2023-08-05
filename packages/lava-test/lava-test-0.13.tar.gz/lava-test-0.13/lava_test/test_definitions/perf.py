# Copyright (c) 2010-2012 Linaro
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
A simple test for the perf performance counters subsystem in Linux. This
currently executes various perf commands built into the perf tool

**URL:** https://code.launchpad.net/~linaro-maintainers/lava-test/lava-test-perf

**Default options:** None
"""

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

DEFAULT_OPTIONS = ""
DEPS = ["bzr", "linux-tools", "stress-dbgsym"]
BZR_REPOS = ["lp:~linaro-maintainers/lava-test/lava-test-perf"]
RUNSTEPS = ["./lava-test-perf/run-perf-test.sh"]
PATTERN = "^(?P<test_case_id>perf[\w\s-]+)\s+:\s+(?P<result>\w+)"
FIXUPS = {
    "PASS": "pass",
    "FAIL": "fail"
}

installer = TestInstaller(deps=DEPS, bzr_repos=BZR_REPOS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, fixupdict=FIXUPS)

testobj = Test(
    test_id="perf",
    installer=installer,
    runner=runner,
    parser=parser)
