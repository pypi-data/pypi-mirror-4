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
A program that performs a series of tests to benchmark the XRender X11
extension.  It also performs the same tests using the Imlib2 library to
provide a base for comparing performance.

**URL:** None

**Default options:** None
"""


import re
import abrek.testdef

class RenderBenchParser(abrek.testdef.AbrekTestParser):
    def parse(self):
        PAT1 = "^Test: (?P<test_case_id>.*)"
        PAT2 = "^Time: (?P<measurement>\d+\.\d+)"
        filename = "testoutput.log"
        pat1 = re.compile(PAT1)
        pat2 = re.compile(PAT2)
        cur_test = None
        with open(filename, 'r') as fd:
            for line in fd:
                match = pat1.search(line)
                if match:
                    cur_test = match.groupdict()['test_case_id']
                else:
                    match = pat2.search(line)
                    if match:
                        d = match.groupdict()
                        d['test_case_id'] = cur_test
                        self.results['test_results'].append(d)

        self.appendtoall({'units':'seconds', 'result':'pass'})

RUNSTEPS = ["render_bench"]

inst = abrek.testdef.AbrekTestInstaller(deps=["render-bench"])
run = abrek.testdef.AbrekTestRunner(RUNSTEPS)
parse = RenderBenchParser()

testobj = abrek.testdef.AbrekTest(testname="render-bench", installer=inst,
                                  runner=run, parser=parse)
