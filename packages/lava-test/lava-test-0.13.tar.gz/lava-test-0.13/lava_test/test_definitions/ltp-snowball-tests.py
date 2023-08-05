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
Snowball specific kernel tests using LTP test framework.

**URL:** http://www.igloocommunity.org/gitweb/?p=testing/snowball-ltp-tests.git;a=summary

**Default options:** dma
"""

import re

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

GIT_REPOS = ['git://igloocommunity.org/git/testing/snowball-ltp-tests.git']
INSTALLSTEPS = ['cd snowball-ltp-tests; make config; make tests; make install']

DEPS = ['git-core', 'make', 'build-essential']

RUNSTEPS = ['cd snowball-ltp-tests/build/opt/ltp && sudo ./runltp -q -p -f $(OPTIONS)']

DEFAULT_OPTIONS = "snowball"

PATTERN = (
    "^(?P<test_case_id>\S+)"
    "\s*(?P<subid>\d+)"
    "\s*(?P<result>\w+)"
    "\s*:\s*(?P<message>.+)")
FIXUPS = {
    "TBROK": "fail",
    "TCONF": "skip",
    "TFAIL": "fail",
    "TINFO": "unknown",
    "TPASS": "pass",
    "TWARN": "unknown"}

class LTPParser(TestParser):

    def parse(self, artifacts):
        filename = artifacts.stdout_pathname
        pat = re.compile(self.pattern)
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                match = pat.search(line)
                if match:
                    results = match.groupdict()
                    subid = results.pop('subid')
                    #The .0 results in ltp are all TINFO, filtering them
                    #should help eliminate meaningless, duplicate results
                    if subid == '0':
                        continue
                    results['test_case_id'] += "." + subid
                    self.results['test_results'].append(
                        self.analyze_test_result(results))

installer = TestInstaller(INSTALLSTEPS, deps=DEPS, git_repos=GIT_REPOS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = LTPParser(PATTERN, fixupdict=FIXUPS)

testobj = Test(
    test_id="ltp-snowball-tests",
    installer=installer,
    runner=runner,
    parser=parser)
