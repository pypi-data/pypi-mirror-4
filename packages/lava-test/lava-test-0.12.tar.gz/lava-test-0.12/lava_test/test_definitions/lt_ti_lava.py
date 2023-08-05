# Copyright (c) 2012 Linaro
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
Validation test suite for TI ARM features on Linux

**URL:** http://git.linaro.org/gitweb?p=people/davelong/lt_ti_lava.git;a=summary

**Default options:** None
"""

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

# Continue the test run in case of failures
DEFAULT_OPTIONS = "-k"

GIT_REPOS = ['git://git.linaro.org/people/davelong/lt_ti_lava.git']

INSTALLSTEPS = ['cd lt_ti_lava && make -C utils']
RUNSTEPS = ['cd lt_ti_lava && make $(OPTIONS) check']
DEPS = ['git-core', 'linux-libc-dev', 'build-essential', 'wget']

# test case id is before ":" and the result is after
# Each test case is separated with a test description beginning with "#"
#
# Example:
# ###
# ### sd_01:
# ### Verify the system sees at least two partitions for SD device #0
# ### ###
# sd_01.0: checking Verify...                                                 pass

PATTERN = (
    "^(?P<test_case_id>[\w/\.]+):"
    "\s+"
    "(?P<message>.+)"
    "\.\.\.\s+"
    "(?P<result>\w+)")

installer = TestInstaller(INSTALLSTEPS, deps=DEPS, git_repos=GIT_REPOS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN)

testobj = Test(
    test_id="lt_ti_lava",
    installer=installer,
    runner=runner,
    parser=parser)
