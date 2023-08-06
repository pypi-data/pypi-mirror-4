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
This script automates the automate installation, execution, and
results parsing for the Peacekeeper browser benchmark.

**URL:** http://clients.futuremark.com/peacekeeper/index.action

**Default options:** firefox
"""


from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

import os

curdir = os.path.realpath(os.path.dirname(__file__))

DEFAULT_OPTIONS = "firefox"
INSTALLSTEPS = ['cp -rf %s/peacekeeper/* .' % curdir]
RUNSTEPS = ['python peacekeeper_runner.py $(OPTIONS)']
DEPS = ['python-ldtp', 'firefox']

PATTERN = "^(?P<result>\w+): Score = (?P<measurement>\d+)"

installer = TestInstaller(INSTALLSTEPS, deps=DEPS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, appendall={'units': 'point'})

testobj = Test(
    test_id="peacekeeper",
    installer=installer,
    runner=runner,
    parser=parser)
