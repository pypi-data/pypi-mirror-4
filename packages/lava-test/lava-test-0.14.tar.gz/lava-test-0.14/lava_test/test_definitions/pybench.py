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
The Pybench test Suite is an open source test suite that provides a
standardized way to measure the performance of Python implementations.

**URL:** http://python.org

**Default options:** None
"""


from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

VERSION = 'r27'
URL = "http://svn.python.org/projects/python/tags/%s/Tools/pybench/" % VERSION
DEFAULT_OPTIONS = ""
INSTALLSTEPS = ["svn export %s" % URL]
RUNSTEPS = ['python pybench/pybench.py $(OPTIONS)']
DEPS = ['subversion']


# test case name is first column and measurement is average column
#
#Test                             minimum  average  operation  overhead
#         BuiltinFunctionCalls:     85ms    151ms    0.30us    0.147ms
#         BuiltinMethodLookup:      68ms    113ms    0.11us    0.171ms

PATTERN = (
    "^\s+"
    "(?P<test_case_id>\w+)"
    ":"
    "\s+(\d+)ms"
    "\s+"
    "(?P<measurement>\d+)ms")


installer = TestInstaller(INSTALLSTEPS, deps=DEPS)
runner = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
parser = TestParser(PATTERN, appendall={'units': 'ms', 'result': 'pass'})

testobj = Test(
    test_id="pybench",
    installer=installer,
    runner=runner,
    parser=parser)
