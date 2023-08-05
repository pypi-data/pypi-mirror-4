# Copyright (c) 2010 Linaro Limited
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

import abrek.testdef

spandex_benchmark = "/usr/share/spandex/bd/benchmarks/opengles2/benchmark_smoke.txt"

INSTALL_STEPS = [
    'sudo add-apt-repository ppa:linaro-maintainers/user-platforms',
    'sudo apt-get update',
    'sudo apt-get install -y --force-yes spandex-gles2 spandex-benchmarks-gles2'
    ]

RUNSTEPS = [
    "spandex-gles2 %s > /dev/null" % spandex_benchmark,
    "python /usr/share/spandex/bd/python/wikireport.py result.txt"
    ]

PATTERN = "^\|\s+(?P<test_case_id>[^|]+?)\s+\|\s+(?P<measurement>\d+(\.\d+)?)"

inst = abrek.testdef.AbrekTestInstaller(INSTALL_STEPS,
                                        deps=["python-software-properties"])
run = abrek.testdef.AbrekTestRunner(RUNSTEPS)
parse = abrek.testdef.AbrekTestParser(PATTERN,
                                      appendall={'units':'reps/s',
                                                 'result':'pass'})

testobj = abrek.testdef.AbrekTest(testname="spandex-gles2", installer=inst,
                                  runner=run, parser=parse)
