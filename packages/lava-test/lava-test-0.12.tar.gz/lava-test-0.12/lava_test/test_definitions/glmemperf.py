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
GLMemPerf is an OpenGL ES 2.0 performance estimation tool that aims to
measure the memory bandwidth characteristics of a graphics implementation.
It performs a number of blit style renders using different texture formats,
sizes, orientations and fragment shaders. The results are given as frames
per second numbers.

**URL:** http://gitorious.org/meego-graphics/glmemperf

**Default Options:** -e shimage
"""


from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

DEFAULT_OPTIONS = "-e shmimage"
RUNSTEPS = ["glmemperf $(OPTIONS)"]
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+) fps"

installer = TestInstaller(deps=["glmemperf"])
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, appendall={'units': 'fps', 'result': 'pass'})

testobj = Test(
    test_id="glmemperf",
    installer=installer,
    runner=runner,
    parser=parser)
