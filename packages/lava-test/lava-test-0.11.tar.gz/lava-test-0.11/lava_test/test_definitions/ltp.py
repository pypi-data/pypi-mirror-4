# Copyright (c) 2010-2012 Linaro
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
The Linux Test Project is a collection of tools for testing Linux with a focus
on the kernel.

**URL:** http://ltp.sourceforge.net

**Default options:** -f syscalls -p -q
"""

import re

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

VERSION = "20120614"
INSTALLSTEPS = ['tar --strip-components=1 -jxf ltp-full-%s.bz2' % VERSION,
                'mkdir build',
                './configure --prefix=$(readlink -f build)',
                'make all',
                'make SKIP_IDCHECK=1 install']
DEPS = ['bzip2', 'flex', 'bison', 'build-essential']
URL = ("http://downloads.sourceforge.net/project/ltp/LTP Source/"
       "ltp-%s/ltp-full-%s.bz2") % (VERSION, VERSION)
MD5 = "1078160b1f962a22f1598edad17293c5"

RUNSTEPS = ['cd build && sudo ./runltp $(OPTIONS)']
DEFAULT_OPTIONS = "-f syscalls -p -q"

PATTERN = (
    "^(?P<test_case_id>\S+)"
    "    (?P<subid>\d+)"
    "  (?P<result>\w+)"
    "  :  (?P<message>.+)")
FIXUPS = {
    "TBROK": "fail",
    "TCONF": "skip",
    "TFAIL": "fail",
    "TINFO": "unknown",
    "TPASS": "pass",
    "TWARN": "unknown"}

class LTPParser(TestParser):

    def parse(self, artifacts):
        filename = artifacts.stdout_pathname
        pat = re.compile(self.pattern)
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                match = pat.search(line)
                if match:
                    results = match.groupdict()
                    subid = results.pop('subid')
                    #The .0 results in ltp are all TINFO, filtering them
                    #should help eliminate meaningless, duplicate results
                    if subid == '0':
                        continue
                    results['test_case_id'] += "." + subid
                    self.results['test_results'].append(
                        self.analyze_test_result(results))

installer = TestInstaller(INSTALLSTEPS, deps=DEPS, url=URL, md5=MD5)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = LTPParser(PATTERN, fixupdict=FIXUPS)

testobj = Test(
    test_id="ltp",
    test_version=VERSION,
    installer=installer,
    runner=runner,
    parser=parser)
