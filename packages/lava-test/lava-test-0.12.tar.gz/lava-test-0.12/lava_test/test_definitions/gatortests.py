# Copyright (c) 2010-2012  Linaro
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
gatortests - tests for streamline gator driver and daemon

"""

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

DEPS = ['gatortests']

RUNSTEPS = ["gatortests"]
DEFAULT_OPTIONS = ""

PATTERN = "^\*\*\*(?P<test_case_id>\w+):\s(?P<result>\w+)\*\*\*"

installer = TestInstaller(deps=DEPS)
runner = TestRunner(RUNSTEPS,default_options=DEFAULT_OPTIONS)
parser = TestParser(pattern=PATTERN)

testobj = Test(
    test_id="gatortests",
    installer=installer,
    runner=runner,
    parser=parser)
