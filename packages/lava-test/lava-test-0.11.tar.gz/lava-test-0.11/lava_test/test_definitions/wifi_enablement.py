# Copyright (c) 2012 Linaro
#
# Author: Ricardo Salveti <rsalveti@linaro.org>
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
The WIFI Enablement test cases helps validating basic wireless
functionality, like if the adapter is available, able to scan, connect and
transfer a file over the network.

**URL:** https://code.launchpad.net/~linaro-foundations/linaro-ubuntu/lava-test-wifi-enablement

**Default Options:** None
"""

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

DEFAULT_OPTIONS = ""
BZR_REPOS = ["lp:~linaro-foundations/linaro-ubuntu/lava-test-wifi-enablement"]
DEPS = [
    "bzr",
    "wpasupplicant",
    "isc-dhcp-client",
    "wireless-tools",
    "net-tools"]
RUNSTEPS = ["cd lava-test-wifi-enablement; sudo bash -x ./run-test.sh"]
PATTERN = "(?P<test_case_id>[a-zA-Z0-9_-]+):\s(?P<result>\w+)"
FIXUPS = {
    "PASS": "pass",
    "FAIL": "fail"
}

installer = TestInstaller(deps=DEPS, bzr_repos=BZR_REPOS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, fixupdict=FIXUPS)

testobj = Test(
    test_id="wifi-enablement",
    installer=installer,
    runner=runner,
    parser=parser)
