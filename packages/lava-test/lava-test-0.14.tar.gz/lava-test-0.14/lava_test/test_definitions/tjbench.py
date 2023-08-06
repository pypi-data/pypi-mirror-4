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
import re

from lava_test.core.installers import TestInstaller
from lava_test.core.parsers import TestParser
from lava_test.core.runners import TestRunner
from lava_test.core.tests import Test

ppm="nightshot_iso_100.ppm"
URL_ppm="http://people.linaro.org/~qzhang/streams/nightshot_iso_100.ppm"

BZR_REPOS = ['lp:~qzhang/libjpeg-turbo/tjbench']

# For the url is from wiki, its name will be saved as with some extra characters
# so it doesn't pass as parameter but use a separate install step.
INSTALLSTEPS = ['wget --no-check-certificate -q "%s" -O %s' % (URL_ppm, ppm)]
DEPS = ['bzr', 'libjpeg-turbo-progs', 'libjpeg-turbo62', 'wget']
DEFAULT_OPTIONS =""
RUNSTEPS = ['./tjbench/tjbench.sh %s' % ppm]

class TjbenchParser(TestParser):
    def parse(self, artifacts):
        filename = artifacts.stdout_pathname
        pat = re.compile(self.pattern)
        tc_id = None
        # Add scale_half prefix or not, the first cmd is half scale, but it's
        # somewhat hard coded
        scale_half = {}
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                match = pat.search(line)
                if match:
                    match_results = match.groupdict()
                    format = match_results.pop('format')
                    bitorder = match_results.pop('bitorder')
                    subsamp = match_results.pop('subsamp')
                    qual = match_results.pop('qual')

                    test_case_id_prefix = '%s_%s_%s_%s' % (format, bitorder,
                            subsamp, qual)
                    if not scale_half.get(test_case_id_prefix):
                        scale_half[test_case_id_prefix] = True
                        test_case_id_prefix = "%s_%s" % (
                                test_case_id_prefix, "scale_half")

                    for perf in ['comp_perf', 'comp_ratio', 'dcomp_perf']:
                        results = { }
                        results["log_filename"] = filename
                        results['test_case_id'] = '%s-%s' % (
                            test_case_id_prefix, perf)
                        results['measurement'] = match_results.pop(perf)
                        if perf == 'comp_ratio':
                            results['units'] = '%'
                        else:
                            results['units'] = 'Mpixels/s'
                        self.results['test_results'].append(
                            self.analyze_test_result(results))

#RGB	TD	4:2:0	95	3136  2352	19.45	15.53	23.30
PATTERN = "^(?P<format>\S+)\s+(?P<bitorder>\w+)\s+(?P<subsamp>[:\w]+)\s+(?P<qual>\d+)\s+\d+\s+\d+\s+(?P<comp_perf>\d+\.\d+)\s+(?P<comp_ratio>\d+\.\d+)\s+(?P<dcomp_perf>\d+\.\d+)"

tjbench_inst = TestInstaller(INSTALLSTEPS, deps=DEPS, bzr_repos=BZR_REPOS)
tjbench_run = TestRunner(RUNSTEPS, default_options=DEFAULT_OPTIONS)
tjbench_parser = TjbenchParser(PATTERN, appendall={'result':'pass'})
testobj = Test(test_id="tjbench",
        installer=tjbench_inst, runner=tjbench_run, parser=tjbench_parser)
