import re
import abrek.testdef

RUNSTEPS = ["glmark2-es2"]

class Glmark2Parser(abrek.testdef.AbrekTestParser):
    def parse(self):
        PAT1 = "^\W+(?P<subtest>.*?)\W+FPS:\W+(?P<measurement>\d+)"
        filename = "testoutput.log"
        pat1 = re.compile(PAT1)
        in_results = False
        cur_test = ""
        with open(filename, 'r') as fd:
            for line in fd.readlines():
                if line.find("Precompilation") != -1:
                    in_results = True
                if in_results == True:
                    match = pat1.search(line)
                    if match:
                        d = match.groupdict()
                        d['test_case_id'] = "%s.%s" % (cur_test, d['subtest'])
                        d.pop('subtest')
                        self.results['test_results'].append(d)
                    else:
                        if line.startswith("==="):
                            in_results = False
                        else:
                            cur_test = line.strip()

        if self.fixupdict:
            self.fixresults(self.fixupdict)
        if self.appendall:
            self.appendtoall(self.appendall)

parse = Glmark2Parser(appendall={'units':'fps', 'result':'pass'})
inst = abrek.testdef.AbrekTestInstaller(deps=["glmark2-es2"])
run = abrek.testdef.AbrekTestRunner(RUNSTEPS)

testobj = abrek.testdef.AbrekTest(testname="glmark2-es2", installer=inst,
                                  runner=run, parser=parse)
