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
The Stream benchmark for measuring memory bandwidth

**URL:** http://www.cs.virginia.edu/stream/

**Default options:** None
"""


from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

URL = "http://www.cs.virginia.edu/stream/FTP/Code/stream.c"
INSTALLSTEPS = ['cc stream.c -O2 -fopenmp -o stream']
DEPS = ['gcc', 'build-essential']
DEFAULT_OPTIONS = ""
RUNSTEPS = ['./stream $(OPTIONS)']
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+\.\d+)"

installer = TestInstaller(INSTALLSTEPS, deps=DEPS, url=URL)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, appendall={'units': 'MB/s', 'result': 'pass'})

testobj = Test(
    test_id="stream",
    installer=installer,
    runner=runner,
    parser=parser)
