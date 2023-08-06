# Copyright (c) 2010,2011 Linaro
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
The firefox benchmark measure the startup time for the firefox browser.

**URL:** https://github.com/janimo/firefox-startup-timing

**Default Options:** None
"""

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

DEFAULT_OPTIONS = ""

GIT_REPOS = ['git://github.com/janimo/firefox-startup-timing.git']
DEPS = ['firefox', 'git-core', 'gcalctool']
RUNSTEPS = [(
    'cd firefox-startup-timing;'
    ' ./firefox_startup_timing.sh $(OPTIONS)')]
PATTERN = "^(?P<test_case_id>\w+):(?P<measurement>\d+)"

installer = TestInstaller(deps=DEPS, git_repos=GIT_REPOS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, appendall={'units': 'ms', 'result': 'pass'})

testobj = Test(
    test_id="firefox",
    installer=installer,
    runner=runner,
    parser=parser)
