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

import datetime

from lava_test.api.delegates import ITestRunner
from lava_test.extcmd import (DisplayDelegate, ExternalCommandWithDelegate)


class TestRunner(ITestRunner):
    """
    Base class for defining an test runner object.

    This class can be used as-is for simple execution with the expectation that
    the run() method will be called from the directory where the test was
    installed. Steps, if used, should handle changing directories from there to
    the directory where the test was extracted if necessary.  This class can
    also be extended for more advanced functionality.

    :ivar steps:
        list of shell commands to execute
    """
    def __init__(self, steps=None, default_options=None):
        self.steps = steps or []
        self.default_options = default_options

    def __repr__(self):
        return "<%s steps=%r>" % (self.__class__.__name__, self.steps)

    def _run_lava_test_steps(self, artifacts, observer, test_options=None):
        stdout = open(artifacts.stdout_pathname, 'at')
        stderr = open(artifacts.stderr_pathname, 'at')
        delegate = DisplayDelegate(stdout, stderr, observer)
        extcmd = ExternalCommandWithDelegate(delegate)
        run_failed = False
        try:
            for cmd in self.steps:
                # should override the test options in the step ?
                if cmd.find("$(OPTIONS)") > 0:
                    # check if test options is provided or use default options
                    if not test_options and self.default_options is None:
                        raise RuntimeError((
                            "Test options is missing."
                            " No default value was provided."))
                    if not test_options:
                        test_options = self.default_options
                    cmd = cmd.replace("$(OPTIONS)", test_options)

                if observer:
                    observer.about_to_run_shell_command(cmd)
                returncode = extcmd.call(cmd, shell=True)
                if observer:
                    observer.did_run_shell_command(cmd, returncode)
                if returncode != 0:
                    run_failed = True
        finally:
            stdout.close()
            stderr.close()
        return run_failed

    def run(self, artifacts, observer=None, test_options=None):
        """
        Run the test program by executing steps in sequence.

        .. seealso::

            :meth:`~lava_test.api.delegates.TestRunner.run`
        """
        self.starttime = datetime.datetime.utcnow()
        run_failed = self._run_lava_test_steps(
            artifacts, observer, test_options)
        self.endtime = datetime.datetime.utcnow()
        return run_failed
