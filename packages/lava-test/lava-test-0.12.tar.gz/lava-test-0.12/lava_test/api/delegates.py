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
:mod:`lava_test.api.delegates` -- Interface classes for test delegates
======================================================================

.. module: lava_test.api.delegates

    :synopsis: Interface classes for test delegates
"""

from abc import abstractmethod, abstractproperty

from lava_test.api import _Interface


class ITestInstaller(_Interface):
    """
    Test installer delegate class.

    Wraps the knowledge on how to install a test. It is most helpful with
    :class:`~lava_test.core.tests.Test` that delegates actual actions to helper
    classes.

    .. versionadded:: 0.2
    """

    @abstractmethod
    def install(self, observer):
        """
        Install the test program.

        :param observer:
            Observer object that makes it possible to monitor the actions
            performed by the test installer.
        :type observer:
            :class:`~lava_test.api.observers.ITestInstallerObserver`

        .. versionadded:: 0.2
        """


class ITestRunner(_Interface):
    """
    Test runner delegate.

    Wraps the knowledge on how to run a test. It is most helpful with
    :class:`lava_test.core.tests.Test` that delegates actual actions to
    helper classes.

    .. versionadded:: 0.2
    """

    @abstractmethod
    def run(self, artifacts, observer, test_options):
        """
        Run the test and create artifacts (typically log files).

        Artifacts must be created in the directory specified by various methods
        and properties of of :class:`lava_test.core.TestArtifacts`.

        :param artifacts:
            Object that describes where to store test run artifacts
        :type artifacts: :class:`~lava_test.core.artifacts.TestArtifacts`.
        :param observer:
            Observer object that makes it possible to monitor the actions
            performed by the test runner.
        :type observer: :class:`~lava_test.api.observers.ITestRunnerObserver`
        :param test_options:
           A string with space separated options to pass to the test.

        :return true if any test step return none-zero return code
        .. versionadded:: 0.2
        """


class ITestParser(_Interface):
    """
    Test artefact parser delegate.

    Wraps the knowledge on how to parse the artifacts of a previous test run.
    It is most helpful with :class:`~lava_test.core.tests.Test` that delegates
    actual actions to helper classes.

        .. versionadded:: 0.2
    """

    @abstractmethod
    def parse(self, artifacts):
        """
        Parse the artifacts of a previous test run and return a dictionary with
        a partial TestRun object.

        :param artifacts:
            Object that describes where to find test run artifacts
        :type artifacts: :class:`~lava_test.core.artifacts.TestArtifacts`.

        .. versionadded:: 0.2
        """

    @abstractproperty
    def results(self):
        """
        Results dictionary to be merged with TestRun object inside the bundle.

        .. seealso::
            :meth:`~lava_test.core.artifacts.TestArtifacts.incorporate_parse_results`

        .. versionadded:: 0.1
        """
