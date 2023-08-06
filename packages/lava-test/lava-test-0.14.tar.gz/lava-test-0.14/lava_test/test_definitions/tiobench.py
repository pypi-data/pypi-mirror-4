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
Tiobench is a multi-threaded I/O benchmark. It is used to measure
system performance in four basic operations: sequential read,
random read, sequential write, and random write.

**URL:** http://sourceforge.net/projects/tiobench/

**Default options:** --block=4096 --block=8192 --threads=2 --numruns=2
"""

"""
"""
import re

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test


VERSION = "0.3.3"
URL = ("http://prdownloads.sourceforge.net/tiobench/"
       "tiobench-%s.tar.gz") % VERSION
MD5 = "bf485bf820e693c79e6bd2a38702a128"
DEFAULT_OPTIONS = "--block=4096 --block=8192 --threads=2 --numruns=2"
INSTALLSTEPS = [
    'tar -zxvf tiobench-%s.tar.gz' % VERSION,
    'cd tiobench-%s && make' % VERSION]
RUNSTEPS = [(
    "cd tiobench-%s && "
    "./tiobench.pl $(OPTIONS)") % VERSION]


class TIObenchTestParser(TestParser):

    def parse(self, artifacts):
        # Pattern to match the test case name
        pattern1 = "(?P<test_id>^(Sequential|Random) (Writes|Reads))"
        # Pattern to match the parameter details and measurement
        pattern2 = (".*?(?P<file_size>\d+)\s+(?P<blks_size>\d+)\s+.*?  "
                    "(?P<measurement>((\d|#)+\.?\d*))")
        filename = "testoutput.log"
        pat1 = re.compile(pattern1)
        pat2 = re.compile(pattern2)
        tc_id = None
        with open(filename) as stream:
            for lineno, line in enumerate(stream, 1):
                match1 = pat1.match(line)
                match2 = pat2.search(line)
                if match1:
                    tc_id = match1.group('test_id').replace(" ", "")
                if match2 and tc_id != None:
                    results = match2.groupdict()
                    blks_size = results.pop('blks_size')
                    filesize = results.pop('file_size')
                    results['test_case_id'] = (
                        '%s_%sMBfilesize_%sbytesblksize') % (
                            tc_id, filesize, blks_size)
                    results["log_filename"] = "testoutput.log"
                    results["log_lineno"] = lineno
                    self.results['test_results'].append(
                        self.analyze_test_result(results))

installer = TestInstaller(INSTALLSTEPS, url=URL, md5=MD5)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TIObenchTestParser(appendall={'units': 'MB/s', 'result': 'pass'})

testobj = Test(
    test_id="tiobench",
    test_version=VERSION,
    installer=installer,
    runner=runner,
    parser=parser)
