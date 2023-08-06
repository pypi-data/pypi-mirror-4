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
:mod:`lava_test.api.core` -- Interface classes for core LAVA Test features
==========================================================================

.. module: lava_test.api.core

    :synopsis: Interface classes for core LAVA Test features
"""

from abc import abstractmethod, abstractproperty

from lava_test.api import _Interface


class ITest(_Interface):
    """
    Abstract test definition.

    Test definitions allow lava-test to install, remove, run and parse log
    files of automatic tests. While the interface can be implemented directly
    you should use :class:`lava_test.core.tests.Test` that implements the core
    logic and allow you to customize the parts that are needed by providing
    delegates implementing :class:`~lava_test.api.delegates.ITestInstaller`,
    :class:`~lava_test.api.delegates.ITestRunner` and
    :class:`~lava_test.api.delegates.ITestParser`.

    .. seealso:: :ref:`wrapping_existing_test_or_benchmark`
    """

    @abstractproperty
    def is_installed(self):
        """
        True if this test is installed

        .. versionadded:: 0.2
        """

    @abstractproperty
    def test_id(self):
        """
        The unique name of this test
        """

    @abstractmethod
    def install(self, observer):
        """
        Install the test program.

        This creates an install directory under the user's XDG_DATA_HOME
        directory to mark that the test is installed.  The installer's
        install() method is then called from this directory to complete any
        test specific install that may be needed.

        :param observer:
            Observer object that makes it possible to monitor the actions
            performed by the test installer.
        :type observer:
            :class:`~lava_test.api.observers.ITestInstallerObserver`

        .. versionadded:: 0.2
        """

    @abstractmethod
    def uninstall(self):
        """
        Remove the test program

        Recursively remove test specific directory under the user's
        ``XDG_DATA_HOME directory``.  This will both mark the test as removed,
        and clean up any files that were downloaded or installed under that
        directory. Dependencies are intentionally not removed by this.

        .. versionadded:: 0.1
        """

    @abstractmethod
    def run(self, observer, test_options):
        """
        Run the test program and store artifacts.

        :param observer:
            Observer object that makes it possible to monitor the actions
            performed by the test runner.
        :type observer: :class:`~lava_test.api.observers.ITestRunnerObserver`
        :param test_options:
            Arbitrary string that was provided by the user.
        :type options: :class:`str`
        :return: Pair with test run artifacts and exit code
        :rtype:
            :class:`~lava_test.core.artifacts.TestArtifacts` and :class:`bool`

        .. versionadded:: 0.2
        .. versionchanged:: 0.3.1
            Added options argument and changed the return type to be a tuple
        """

    @abstractmethod
    def parse(self, artifacts):
        """
        Parse the artifacts of an earlier run.

        :param artifacts: Object that describes which files should be parsed.
        :type artifacts: :class:`~lava_test.core.artifacts.TestArtifacts`
        :return:
            A dictionary with all the parsed data. In particular this is a
            TestRun part of the dashboard bundle so it should have the
            test_results list of all the results parsed from the artifacts.
        :rtype: :class:`dict`

        .. versionadded:: 0.2
        """


class ITestProvider(_Interface):
    """
    Source of ITest instances.

    Test providers can be used to make lava-test aware of arbitrary collections
    of tests that can be installed and invoked. Internally lava-test uses this
    class to offer built-in tests (via the
    :class:`~lava_test.providers.BuiltInProvider`), out-of-tree tests (via the
    :class:`~lava_test.providers.PkgResourcesProvider`) and declarative tests
    (via the :class:`~lava_test.providers.RegistryProvider`).

    Normally this is not something you would need to implement. If you have a
    large collection of existing tests that can be somehow adapted in bulk, or
    you have your own internal registry of tests that could be adapted this way
    then you might use this interface to simplify test discovery.

    Test providers need to be registered using pkg-resources entry-point
    feature and then added to the lava-test configuration file. See
    :class:`lava_test.config.LavaTestConfig` for details.

    .. versionadded:: 0.2
    """

    @abstractmethod
    def __init__(self, config):
        """
        Initialize test provider with the specified configuration object. The
        configuration object is obtained from the test tool providers registry.
        """

    @abstractmethod
    def __iter__(self):
        """
        Iterates over instances of ITest exposed by this provider
        """

    @abstractmethod
    def __getitem__(self, test_id):
        """
        Return an instance of ITest with the specified id
        """

    @abstractproperty
    def description(self):
        """
        The description string used by `lava-test list-tests`
        """


__all__ = ['ITest', 'ITestProvider']
