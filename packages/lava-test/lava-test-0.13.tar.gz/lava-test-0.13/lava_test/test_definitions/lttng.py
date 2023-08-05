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
The lttng test executes lttng-tools test suite and reports the result.

**URL:** https://code.launchpad.net/~linaro-foundations/linaro-ubuntu/lava-test-lttng

**Default options:** None
"""

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

DEFAULT_OPTIONS = ""

BZR_REPOS=["lp:~linaro-foundations/linaro-ubuntu/lava-test-lttng"]
INSTALLSTEPS = ["apt-get build-dep lttng-tools --yes"]
DEPS = ["bzr", "linux-headers-$(uname -r)", "lttng-modules-dkms"]
RUNSTEPS = ["cd lava-test-lttng; sudo bash -x ./run-test.sh"]
PATTERN = "^(?P<test_case_id>[\w:()]+)\s+\-\s+(?P<result>\w+$)"

installer = TestInstaller(INSTALLSTEPS, deps=DEPS, bzr_repos=BZR_REPOS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN)

testobj = Test(
    test_id="lttng",
    installer=installer,
    runner=runner,
    parser=parser)
