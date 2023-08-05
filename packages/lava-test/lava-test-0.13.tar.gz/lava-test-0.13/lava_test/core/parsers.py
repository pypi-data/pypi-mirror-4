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

import decimal
import os
import re

from lava_test.api.delegates import ITestParser


class TestParser(ITestParser):
    """
    Base class for defining a test parser

    This class can be used as-is for simple results parsers, but will likely
    need to be extended slightly for many.  If used as it is, the parse()
    method should be called while already in the results directory and assumes
    that a file for test output will exist called testoutput.log.

    :ivar pattern:
        regexp pattern to identify important elements of test output For
        example: If your testoutput had lines that look like: "test01: PASS"
        then you could use a pattern like this:
        "^(?P<testid>\w+):\W+(?P<result>\w+)" This would result in
        identifying "test01" as testid and "PASS" as result. Once parse()
        has been called, self.results.test_results[] contains a list of
        dicts of all the key,value pairs found for each test result.

    :ivar fixupdict:
        Dict of strings to convert test results to standard strings For
        example: if you want to standardize on having pass/fail results in
        lower case, but your test outputs them in upper case, you could use a
        fixupdict of something like: {'PASS':'pass','FAIL':'fail'}

    :ivar appendall:
        Append a dict to the test_results entry for each result.
        For example: if you would like to add units="MB/s" to each result:
        appendall={'units':'MB/s'}

    :ivar results:
        Dictionary of data that was scrubbed from the log file for this test
        run. Most notably it contains the test_results array.
    """
    def __init__(self, pattern=None, fixupdict=None, appendall={}):
        if pattern is not None:
            try:
                re.compile(pattern)
            except Exception as ex:
                raise ValueError(
                    "Invalid regular expression %r: %s", pattern, ex)
        self._results = {'test_results': []}
        self.pattern = pattern
        self.fixupdict = fixupdict
        self.appendall = appendall

    def __repr__(self):
        return "<%s pattern=%r fixupdict=%r appendall=%r>" % (
            self.__class__.__name__,
            self.pattern, self.fixupdict, self.appendall)

    @property
    def results(self):
        return self._results

    def parse(self, artifacts):
        if os.path.exists(artifacts.stdout_pathname):
            return self.parse_pathname(
                artifacts.stdout_pathname,
                os.path.relpath(artifacts.stdout_pathname,
                                artifacts.results_dir))
        if os.path.exists(artifacts.stderr_pathname):
            return self.parse_pathname(
                artifacts.stderr_pathname,
                os.path.relpath(artifacts.stderr_pathname,
                                artifacts.results_dir))

    def parse_pathname(self, pathname, relative_pathname=None):
        with open(pathname, 'rt') as stream:
            for lineno, line in enumerate(stream, 1):
                match = re.search(self.pattern, line)
                if not match:
                    continue
                data = match.groupdict()
                data["log_filename"] = relative_pathname or pathname
                data["log_lineno"] = lineno
                self._results['test_results'].append(
                    self.analyze_test_result(data))
        return self.results

    @property
    def badchars(self):
        return "[^a-zA-Z0-9\._-]"

    def analyze_test_result(self, data):
        """
        Analyze sigle match (typically single line) and convert it into a
        proper test result object.

        Currently this method does the following transformations:
            * measurement is converted to decimal if present
            * test_case_id is rewritten to strip badchars
            * test_case_id is rewritten to convert spaces to underscores
            * result is transformed using fixuptdict, if defined
            * appendall information is added, if defined
        """
        if 'measurement' in data:
            try:
                data['measurement'] = decimal.Decimal(data['measurement'])
            except decimal.InvalidOperation:
                del data['measurement']
        if 'test_case_id' in data:
            data['test_case_id'] = re.sub(self.badchars, "",
                                          data['test_case_id'])
            data['test_case_id'] = data['test_case_id'].replace(" ", "_")
        if 'result' in data and self.fixupdict:
            data['result'] = self.fixupdict[data['result']]
        if self.appendall:
            data.update(self.appendall)
        return data


class NativeTestParser(ITestParser):
    """
    Unfinished native test parser.

    This was meant to be a pass-through for tests that directly create bundles
    """
    def __init__(self, test_def):
        self.test_def = test_def

    def parse(self, artifacts):
        raise NotImplementedError()

    def results(self):
        raise NotImplementedError()
