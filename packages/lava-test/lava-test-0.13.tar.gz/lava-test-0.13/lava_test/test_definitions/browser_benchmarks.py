# Copyright (c) 2012 Linaro
#
# Author: John Rigby <john.rigby@linaro.org>
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
Use Selenium WebDriver to automatically run browser benchmarks
and scrape the results.

**URL:** https://code.launchpad.net/~linaro-foundations/linaro-ubuntu/lava-test-browser-benchmarks

**Default Options:** None
"""

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

DEFAULT_OPTIONS = ""
BZR_REPOS = ["lp:~linaro-foundations/linaro-ubuntu/lava-test-browser-benchmarks"]
DEPS = ["bzr", "python-pip", "chromium-browser", "firefox"]
INSTALLSTEPS = ['pip install selenium']
RUNSTEPS = ["cd lava-test-browser-benchmarks; bash -x ./run-test.sh; pwd"]
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+)"

installer = TestInstaller(INSTALLSTEPS, deps=DEPS, bzr_repos=BZR_REPOS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, appendall={'units': 'score', 'result': 'pass'})

testobj = Test(
    test_id="browser-benchmarks",
    installer=installer,
    runner=runner,
    parser=parser)
