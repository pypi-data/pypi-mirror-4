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
Linaro Power Management QA test suite

**URL:** http://git.linaro.org/gitweb?p=tools/pm-qa.git;a=summary

**Default options:** None
"""

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

# Continue the test run in case of failures
DEFAULT_OPTIONS = "-k"

GIT_REPOS = ['git://git.linaro.org/tools/pm-qa.git']
INSTALLSTEPS = ['cd pm-qa && make -C utils']
RUNSTEPS = ['cd pm-qa && make $(OPTIONS) check']
DEPS = ['git-core', 'linux-libc-dev', 'build-essential']

# test case name is before  ":" , the test log is between ":" and "...",
# the result is after "..."
# Each test case is separated with a test description beginning with "#"

# Example:
####
#### cpufreq_02:
#### test the cpufreq framework is available for governor
####
#cpufreq_02.0/cpu0: checking scaling_available_governors exists...        pass
#cpufreq_02.1/cpu0: checking scaling_governor exists...                   pass
#cpufreq_02.0/cpu1: checking scaling_available_governors exists...        pass
#cpufreq_02.1/cpu1: checking scaling_governor exists...                   pass

PATTERN = (
    "^(?P<test_case_id>[\w/\.]+):"
    "\s+"
    "(?P<message>.+)"
    "\.\.\.\s+"
    "(?P<result>\w+)")

installer = TestInstaller(INSTALLSTEPS, deps=DEPS, git_repos=GIT_REPOS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, appendall={'result': 'pass'})

testobj = Test(
    test_id="pwrmgmt",
    installer=installer,
    runner=runner,
    parser=parser)
