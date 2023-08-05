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
#

"""
X11perf is an xlib based benchmark to see how fast an X server can execute various tests

**URL:** http://cgit.freedesktop.org/xorg/app/x11perf/

**Default options:** -repeat 3 -aa10text -aa24text -aatrapezoid300 -aatrap2x300 -copypixwin500 -copypixpix500 -comppixwin500 -shmput500 -shmputxy500 -scroll500
"""



from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test


x11perf_options = "-repeat 3"

x11perf_tests = [
    # Antialiased text (using XFT)
    "-aa10text",
    "-aa24text",

    # Antialiased drawing (using XRENDER)
    "-aatrapezoid300",
    "-aatrap2x300",

    # Normal blitting
    "-copypixwin500",
    "-copypixpix500",

    # Composited blitting
    "-comppixwin500",

    # SHM put image
    "-shmput500",
    "-shmputxy500",

    "-scroll500",
]

DEFAULT_OPTIONS = "%s %s" % (x11perf_options,  " ".join(x11perf_tests))
RUNSTEPS = ["x11perf $(OPTIONS)"]
PATTERN = "trep @.*\(\W*(?P<measurement>\d+.\d+)/sec\):\W+(?P<test_case_id>.+)"

installer = TestInstaller(deps=["x11-apps"])
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, appendall={'units': 'reps/s', 'result': 'pass'})

testobj = Test(
    test_id="x11perf",
    installer=installer,
    runner=runner,
    parser=parser)
